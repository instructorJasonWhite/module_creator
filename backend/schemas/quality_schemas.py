from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QualityMetric(str, Enum):
    """Types of quality metrics."""

    READABILITY = "readability"
    COMPLEXITY = "complexity"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    ENGAGEMENT = "engagement"
    ACCESSIBILITY = "accessibility"


class QualityLevel(str, Enum):
    """Quality assessment levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


class QualityScore(BaseModel):
    """Quality score for a specific metric."""

    metric: QualityMetric
    score: float
    level: QualityLevel
    details: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)


class QualityAssessment(BaseModel):
    """Complete quality assessment for content."""

    assessment_id: UUID = Field(default_factory=uuid4)
    content_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float
    overall_level: QualityLevel
    metrics: List[QualityScore] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessibilityCheck(BaseModel):
    """Accessibility assessment results."""

    wcag_level: str
    passed_criteria: List[str] = Field(default_factory=list)
    failed_criteria: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class EngagementMetrics(BaseModel):
    """Content engagement metrics."""

    interactivity_score: float
    visual_appeal: float
    content_flow: float
    user_interest: float
    suggestions: List[str] = Field(default_factory=list)


class CompletenessCheck(BaseModel):
    """Content completeness assessment."""

    required_elements: List[str] = Field(default_factory=list)
    missing_elements: List[str] = Field(default_factory=list)
    optional_elements: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AccuracyCheck(BaseModel):
    """Content accuracy assessment."""

    factual_accuracy: float
    technical_accuracy: float
    consistency_score: float
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class QualityCheckRequest(BaseModel):
    """Request for quality assessment."""

    content_id: UUID
    content_type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    requirements: Dict[str, Any] = Field(default_factory=dict)


class QualityCheckResult(BaseModel):
    """Result of quality assessment."""

    request_id: UUID
    status: str
    assessment: Optional[QualityAssessment] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None


class QualityImprovement(BaseModel):
    """Suggested quality improvements."""

    content_id: UUID
    assessment_id: UUID
    improvements: List[Dict[str, Any]] = Field(default_factory=list)
    priority: str
    estimated_effort: str
    impact: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
