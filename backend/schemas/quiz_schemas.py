from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """Types of quiz questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    MATCHING = "matching"
    FILL_IN_BLANK = "fill_in_blank"


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class BloomTaxonomyLevel(str, Enum):
    """Bloom's Taxonomy levels."""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class AnswerOption(BaseModel):
    """Answer option for multiple choice questions."""

    option_id: UUID = Field(default_factory=uuid4)
    text: str
    is_correct: bool
    explanation: Optional[str] = None
    feedback: Optional[str] = None


class Question(BaseModel):
    """Quiz question model."""

    question_id: UUID = Field(default_factory=uuid4)
    type: QuestionType
    text: str
    difficulty: DifficultyLevel
    bloom_level: BloomTaxonomyLevel
    options: List[AnswerOption] = Field(default_factory=list)
    correct_answer: str
    explanation: str
    hints: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Quiz(BaseModel):
    """Complete quiz model."""

    quiz_id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    module_id: UUID
    questions: List[Question] = Field(default_factory=list)
    difficulty: DifficultyLevel
    total_points: int
    passing_score: int
    time_limit: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QuizGenerationRequest(BaseModel):
    """Request for quiz generation."""

    module_id: UUID
    content: str
    difficulty: DifficultyLevel
    question_count: int
    question_types: List[QuestionType] = Field(default_factory=list)
    bloom_levels: List[BloomTaxonomyLevel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QuizGenerationResult(BaseModel):
    """Result of quiz generation."""

    request_id: UUID
    status: str
    quiz: Optional[Quiz] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None


class QuizValidationResult(BaseModel):
    """Result of quiz validation."""

    quiz_id: UUID
    is_valid: bool
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    difficulty_distribution: Dict[DifficultyLevel, int] = Field(default_factory=dict)
    bloom_distribution: Dict[BloomTaxonomyLevel, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QuizAttempt(BaseModel):
    """User's attempt at a quiz."""

    attempt_id: UUID = Field(default_factory=uuid4)
    quiz_id: UUID
    user_id: UUID
    answers: Dict[UUID, str] = Field(default_factory=dict)
    score: float
    passed: bool
    time_taken: Optional[float] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    feedback: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QuizAnalytics(BaseModel):
    """Analytics for a quiz."""

    quiz_id: UUID
    total_attempts: int
    average_score: float
    pass_rate: float
    average_time: Optional[float] = None
    difficulty_analysis: Dict[DifficultyLevel, float] = Field(default_factory=dict)
    question_analysis: Dict[UUID, Dict[str, Any]] = Field(default_factory=dict)
    user_feedback: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
