from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ContentComplexity(str, Enum):
    """Content complexity levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DocumentSection(BaseModel):
    """Represents a section of a document."""

    section_id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    level: int = Field(ge=1, le=6)  # Heading level (1-6)
    keywords: List[str] = Field(default_factory=list)
    complexity: ContentComplexity
    parent_section_id: Optional[UUID] = None
    child_sections: List[UUID] = Field(default_factory=list)


class DocumentAnalysis(BaseModel):
    """Complete document analysis results."""

    document_id: UUID
    title: str
    document_type: DocumentType
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    total_pages: Optional[int] = None
    sections: List[DocumentSection] = Field(default_factory=list)
    main_topics: List[str] = Field(default_factory=list)
    key_concepts: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    overall_complexity: ContentComplexity
    metadata: Dict[str, Any] = Field(default_factory=dict)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentProcessingStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentProcessingResult(BaseModel):
    """Result of document processing."""

    document_id: UUID
    status: DocumentProcessingStatus
    analysis: Optional[DocumentAnalysis] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None
