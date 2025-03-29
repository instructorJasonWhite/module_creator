from datetime import datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """Base message schema with common fields."""

    message_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = Field(default=0, ge=0)
    status: Literal["pending", "processing", "completed", "failed"] = "pending"


class ContentGenerationRequest(BaseMessage):
    """Schema for content generation request messages."""

    document_id: UUID
    module_type: str
    parameters: Dict[str, Any]
    user_id: UUID
    priority: int = Field(default=1, ge=1, le=5)


class ContentGenerationResponse(BaseMessage):
    """Schema for content generation response messages."""

    request_id: UUID
    output_id: Optional[UUID] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


class AgentTask(BaseMessage):
    """Schema for individual agent task messages."""

    agent_type: str
    task_data: Dict[str, Any]
    parent_request_id: UUID
    dependencies: list[UUID] = Field(default_factory=list)


class AgentResponse(BaseMessage):
    """Schema for agent response messages."""

    task_id: UUID
    result: Dict[str, Any]
    error: Optional[str] = None
