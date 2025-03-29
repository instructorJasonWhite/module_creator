import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Type
from uuid import UUID

from ..database.redis_config import get_redis_connection, retry_operation
from ..queue.queue_manager import QueueManager
from ..schemas.message_schemas import AgentResponse, AgentTask
from .base_agent import AgentError, BaseAgent


class AgentCoordinator:
    """Coordinates communication and task routing between agents."""

    def __init__(self):
        self.redis = get_redis_connection()
        self.queue_manager = QueueManager()
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent.coordinator")

        # Set up dead letter queue
        self.dead_letter_queue = self.queue_manager.get_queue("dead_letter")

        # Initialize message tracing
        self._initialize_tracing()

    def _initialize_tracing(self):
        """Initialize message tracing system."""
        self.trace_key = "message_trace"
        if not self.redis.exists(self.trace_key):
            self.redis.hset(
                self.trace_key,
                mapping={
                    "created_at": datetime.utcnow().isoformat(),
                    "total_messages": 0,
                    "failed_messages": 0,
                },
            )

    def register_agent(self, agent: BaseAgent):
        """Register a new agent with the coordinator."""
        self.agents[agent.agent_id] = agent
        self.logger.info(
            f"Registered agent {agent.agent_id} of type {agent.__class__.__name__}"
        )

    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the coordinator."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent {agent_id}")

    async def route_task(self, task: AgentTask) -> UUID:
        """
        Route a task to the appropriate agent.
        Args:
            task: The task to route
        Returns:
            UUID: Message ID
        """
        # Find suitable agent
        agent = self._find_suitable_agent(task)
        if not agent:
            raise AgentError(
                f"No suitable agent found for task type: {task.agent_type}"
            )

        # Create message trace
        trace_id = self._create_message_trace(task)

        try:
            # Route task to agent
            message_id = await self.queue_manager.enqueue_message(
                "agent_task", task, timeout=3600  # 1 hour timeout
            )

            # Update trace with routing info
            self._update_message_trace(trace_id, "routed", message_id=message_id)

            return message_id
        except Exception as e:
            # Update trace with error
            self._update_message_trace(trace_id, "failed", error=str(e))
            # Move to dead letter queue
            await self._handle_failed_task(task, str(e))
            raise

    def _find_suitable_agent(self, task: AgentTask) -> Optional[BaseAgent]:
        """Find an agent suitable for processing the task."""
        for agent in self.agents.values():
            if agent.__class__.__name__ == task.agent_type:
                return agent
        return None

    @retry_operation
    def _create_message_trace(self, task: AgentTask) -> str:
        """Create a new message trace entry."""
        trace_id = str(UUID())
        trace_data = {
            "trace_id": trace_id,
            "task_id": str(task.message_id),
            "agent_type": task.agent_type,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "parent_request_id": str(task.parent_request_id),
        }

        self.redis.hset(f"trace:{trace_id}", mapping=trace_data)

        # Update trace statistics
        self.redis.hincrby(self.trace_key, "total_messages", 1)

        return trace_id

    @retry_operation
    def _update_message_trace(
        self,
        trace_id: str,
        status: str,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """Update a message trace entry."""
        update_data = {"status": status, "updated_at": datetime.utcnow().isoformat()}

        if message_id:
            update_data["message_id"] = message_id
        if error:
            update_data["error"] = error
            self.redis.hincrby(self.trace_key, "failed_messages", 1)

        self.redis.hmset(f"trace:{trace_id}", update_data)

    async def _handle_failed_task(self, task: AgentTask, error: str):
        """Handle failed tasks by moving them to the dead letter queue."""
        failed_task = {
            "task": task.model_dump(),
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.queue_manager.enqueue_message(
            "dead_letter", failed_task, timeout=3600
        )

    def get_message_trace(self, trace_id: str) -> Optional[Dict]:
        """Get the trace information for a message."""
        trace_data = self.redis.hgetall(f"trace:{trace_id}")
        return trace_data if trace_data else None

    def get_trace_statistics(self) -> Dict:
        """Get message tracing statistics."""
        return self.redis.hgetall(self.trace_key)

    async def shutdown(self):
        """Shutdown the coordinator and all registered agents."""
        for agent in self.agents.values():
            await agent.shutdown()
        self.agents.clear()
        self.logger.info("Agent coordinator shutdown complete")
