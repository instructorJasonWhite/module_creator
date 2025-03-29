import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import redis
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    name: str
    description: str
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    redis_url: str
    prompt_template: str


class BaseAgent(ABC):
    """Base class for all agents in the system"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.redis_client = redis.from_url(config.redis_url)
        self.llm = ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", config.prompt_template), ("human", "{input}")]
        )
        self.logger = logging.getLogger(f"agent.{config.name}")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass

    async def send_message(
        self, target_agent: str, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a message to another agent"""
        message_id = f"msg:{target_agent}:{self.config.name}:{json.dumps(message)}"
        self.redis_client.rpush(f"agent:{target_agent}:inbox", message_id)
        return {"status": "sent", "message_id": message_id}

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive a message from the agent's inbox"""
        message_id = self.redis_client.lpop(f"agent:{self.config.name}:inbox")
        if message_id:
            return json.loads(message_id.split(":", 1)[1])
        return None

    def _format_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format the prompt template with input data"""
        return self.prompt_template.format_messages(input=input_data)

    async def _execute_llm(self, messages: list[BaseMessage]) -> str:
        """Execute the LLM with the given messages"""
        try:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
        except Exception as e:
            self.logger.error(f"Error executing LLM: {str(e)}")
            raise

    def _validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the output of the agent"""
        # Implement validation logic specific to each agent
        return True

    async def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors that occur during processing"""
        self.logger.error(f"Error in agent {self.config.name}: {str(error)}")
        return {"status": "error", "agent": self.config.name, "error": str(error)}
