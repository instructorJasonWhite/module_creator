from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of generated content."""

    TEXT = "text"
    EXAMPLE = "example"
    EXERCISE = "exercise"
    VISUAL = "visual"
    INTERACTIVE = "interactive"


class ContentFormat(str, Enum):
    """Formats for generated content."""

    MARKDOWN = "markdown"
    HTML = "html"
    PLAINTEXT = "plaintext"


class ContentStyle(str, Enum):
    """Styles for content presentation."""

    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"


class GeneratedContent(BaseModel):
    """Base model for generated content."""

    content_id: UUID = Field(default_factory=uuid4)
    type: ContentType
    format: ContentFormat
    style: ContentStyle
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExampleContent(GeneratedContent):
    """Generated example content."""

    concept: str
    explanation: str
    steps: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)


class ExerciseContent(GeneratedContent):
    """Generated exercise content."""

    question: str
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    explanation: str
    difficulty_level: str
    hints: List[str] = Field(default_factory=list)


class VisualContent(GeneratedContent):
    """Generated visual content."""

    title: str
    description: str
    type: str  # diagram, chart, graph, etc.
    data: Dict[str, Any]
    style: Dict[str, Any] = Field(default_factory=dict)


class InteractiveContent(GeneratedContent):
    """Generated interactive content."""

    component_type: str
    configuration: Dict[str, Any]
    dependencies: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)


class ContentGenerationRequest(BaseModel):
    """Request for content generation."""

    module_id: UUID
    content_type: ContentType
    topic: str
    difficulty_level: str
    target_audience: str
    style: ContentStyle
    format: ContentFormat
    requirements: Dict[str, Any] = Field(default_factory=dict)


class ContentGenerationResult(BaseModel):
    """Result of content generation."""

    request_id: UUID
    status: str
    content: Optional[GeneratedContent] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None


class ContentValidationResult(BaseModel):
    """Result of content validation."""

    content_id: UUID
    is_valid: bool
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    readability_score: Optional[float] = None
    complexity_score: Optional[float] = None
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)
