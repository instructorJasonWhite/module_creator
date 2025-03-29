from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Types of assets that can be embedded in HTML."""

    CSS = "css"
    JAVASCRIPT = "javascript"
    IMAGE = "image"
    FONT = "font"
    ICON = "icon"
    STYLE = "style"


class Asset(BaseModel):
    """Model for embedded assets in HTML output."""

    asset_id: UUID = Field(default_factory=uuid4)
    type: AssetType
    content: str
    name: str
    size: int
    mime_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HTMLTemplate(BaseModel):
    """Model for HTML template."""

    template_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    content: str
    assets: List[Asset] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HTMLOutput(BaseModel):
    """Model for generated HTML output."""

    output_id: UUID = Field(default_factory=uuid4)
    module_id: UUID
    title: str
    content: str
    assets: List[Asset] = Field(default_factory=list)
    template_id: UUID
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HTMLGenerationRequest(BaseModel):
    """Request for HTML generation."""

    module_id: UUID
    template_id: Optional[UUID] = None
    customization: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HTMLGenerationResult(BaseModel):
    """Result of HTML generation."""

    request_id: UUID
    status: str
    output: Optional[HTMLOutput] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[datetime] = None


class HTMLValidationResult(BaseModel):
    """Result of HTML validation."""

    output_id: UUID
    is_valid: bool
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    file_size: int
    asset_count: int
    browser_compatibility: Dict[str, bool] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HTMLPreview(BaseModel):
    """Model for HTML preview."""

    preview_id: UUID = Field(default_factory=uuid4)
    output_id: UUID
    url: str
    expires_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HTMLAnalytics(BaseModel):
    """Analytics for HTML output."""

    output_id: UUID
    total_views: int
    average_load_time: float
    browser_usage: Dict[str, int] = Field(default_factory=dict)
    device_usage: Dict[str, int] = Field(default_factory=dict)
    user_feedback: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
