import logging
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    model_config = ConfigDict(protected_namespaces=())

    name: str
    description: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    prompt_template: Optional[str] = None


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"Initialized {config.name} agent")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        raise NotImplementedError("Subclasses must implement process()")

    async def _execute_llm(self, messages: list) -> str:
        """Execute the language model with the given messages"""
        raise NotImplementedError("Subclasses must implement _execute_llm()")

    async def send_message(self, target: str, message: Dict[str, Any]) -> None:
        """Send a message to another agent"""
        self.logger.debug(f"Sending message to {target}: {message}")

    async def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors during processing"""
        self.logger.error(f"Error in {self.config.name}: {str(error)}", exc_info=True)
        return {
            "status": "error",
            "agent": self.config.name,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
        }

    async def _get_model_settings(self) -> Dict[str, Any]:
        """Get the model settings for the agent"""
        try:
            from app.services.model_service import get_active_model

            model_settings = await get_active_model()
            if not model_settings:
                raise ValueError(f"No active model found")
            return model_settings
        except Exception as e:
            self.logger.error(f"Error getting model settings: {str(e)}", exc_info=True)
            raise
