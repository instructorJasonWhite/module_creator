import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..database.redis_config import get_redis_connection, retry_operation
from ..schemas.message_schemas import AgentResponse, AgentTask


class AgentState(Enum):
    """Enum for agent states."""

    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentError(Exception):
    """Base exception for agent errors."""

    pass


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: int = 1,
    ):
        self.agent_id = agent_id or str(uuid4())
        self.config = config or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.state = AgentState.IDLE
        self.redis = get_redis_connection()

        # Set up logging
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        # Initialize health metrics
        self.health_metrics = {
            "start_time": datetime.utcnow().isoformat(),
            "tasks_processed": 0,
            "errors": 0,
            "last_error": None,
            "last_success": None,
        }

        # Initialize state storage
        self._initialize_state()

    def _initialize_state(self):
        """Initialize agent state in Redis."""
        state_key = f"agent:{self.agent_id}:state"
        self.redis.hset(
            state_key,
            mapping={
                "agent_id": self.agent_id,
                "agent_type": self.__class__.__name__,
                "state": self.state.value,
                "config": json.dumps(self.config),
                "health_metrics": json.dumps(self.health_metrics),
            },
        )

    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a task and return a response.
        Args:
            task: The task to process
        Returns:
            AgentResponse: The response from processing the task
        """
        pass

    async def handle_task(self, task: AgentTask) -> AgentResponse:
        """
        Handle a task with error handling and retries.
        Args:
            task: The task to handle
        Returns:
            AgentResponse: The response from processing the task
        """
        self.state = AgentState.PROCESSING
        self._update_state()

        try:
            response = await self.process_task(task)
            self._update_health_metrics(success=True)
            return response
        except Exception as e:
            self._update_health_metrics(success=False, error=str(e))
            raise AgentError(f"Task processing failed: {str(e)}")
        finally:
            self.state = AgentState.IDLE
            self._update_state()

    @retry_operation
    def _update_state(self):
        """Update agent state in Redis."""
        state_key = f"agent:{self.agent_id}:state"
        self.redis.hset(
            state_key,
            mapping={
                "state": self.state.value,
                "last_updated": datetime.utcnow().isoformat(),
                "health_metrics": json.dumps(self.health_metrics),
            },
        )

    def _update_health_metrics(self, success: bool, error: Optional[str] = None):
        """Update agent health metrics."""
        self.health_metrics["tasks_processed"] += 1
        if success:
            self.health_metrics["last_success"] = datetime.utcnow().isoformat()
        else:
            self.health_metrics["errors"] += 1
            self.health_metrics["last_error"] = error
            self.health_metrics["last_error_time"] = datetime.utcnow().isoformat()

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of the agent."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "state": self.state.value,
            "health_metrics": self.health_metrics,
            "config": self.config,
        }

    async def shutdown(self):
        """Gracefully shutdown the agent."""
        self.state = AgentState.SHUTDOWN
        self._update_state()
        self.logger.info(f"Agent {self.agent_id} shutting down")

    def __del__(self):
        """Cleanup when the agent is destroyed."""
        try:
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Error during agent cleanup: {str(e)}")
