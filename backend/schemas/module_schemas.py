from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ModuleType(str, Enum):
    """Types of learning modules."""

    INTRODUCTION = "introduction"
    CONCEPT = "concept"
    EXAMPLE = "example"
    EXERCISE = "exercise"
    QUIZ = "quiz"
    SUMMARY = "summary"


class LearningObjective(BaseModel):
    """Learning objective for a module."""

    objective_id: UUID = Field(default_factory=uuid4)
    description: str
    bloom_level: str  # Bloom's taxonomy level
    prerequisites: List[UUID] = Field(default_factory=list)
    assessment_criteria: List[str] = Field(default_factory=list)


class ModuleContent(BaseModel):
    """Content structure for a module."""

    content_id: UUID = Field(default_factory=uuid4)
    type: ModuleType
    title: str
    content: str
    learning_objectives: List[LearningObjective] = Field(default_factory=list)
    estimated_duration: int  # in minutes
    difficulty_level: str
    interactive_elements: List[str] = Field(default_factory=list)
    visual_aids: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    exercises: List[str] = Field(default_factory=list)


class Module(BaseModel):
    """Complete learning module structure."""

    module_id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    level: int
    prerequisites: List[UUID] = Field(default_factory=list)
    contents: List[ModuleContent] = Field(default_factory=list)
    total_duration: int  # in minutes
    difficulty_level: str
    learning_objectives: List[LearningObjective] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModulePlan(BaseModel):
    """Complete learning module plan."""

    plan_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    title: str
    description: str
    target_audience: str
    modules: List[Module] = Field(default_factory=list)
    total_duration: int  # in minutes
    difficulty_level: str
    prerequisites: List[str] = Field(default_factory=list)
    learning_path: List[UUID] = Field(
        default_factory=list
    )  # Ordered list of module IDs
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModulePlanningStatus(str, Enum):
    """Status of module planning process."""

    PENDING = "pending"
    PLANNING = "planning"
    COMPLETED = "completed"
    FAILED = "failed"


class ModulePlanningResult(BaseModel):
    """Result of module planning process."""

    plan_id: UUID
    status: ModulePlanningStatus
    plan: Optional[ModulePlan] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None
