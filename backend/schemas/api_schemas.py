from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserRole(str, Enum):
    """User roles for authorization."""

    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    GUEST = "guest"


class User(BaseModel):
    """User model for authentication and authorization."""

    user_id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(BaseModel):
    """Request model for user creation."""

    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.GUEST
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """Request model for user updates."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class Token(BaseModel):
    """JWT token model."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Data stored in JWT token."""

    user_id: UUID
    email: EmailStr
    role: UserRole
    exp: datetime


class APIKey(BaseModel):
    """API key model for external access."""

    key_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    key: str
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIKeyCreate(BaseModel):
    """Request model for API key creation."""

    name: str
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileUpload(BaseModel):
    """Request model for file uploads."""

    file_name: str
    content_type: str
    size: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileInfo(BaseModel):
    """Model for file information."""

    file_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    file_name: str
    content_type: str
    size: int
    url: HttpUrl
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RateLimit(BaseModel):
    """Rate limit configuration."""

    requests_per_minute: int = 60
    burst_size: int = 10
    window_seconds: int = 60


class RateLimitInfo(BaseModel):
    """Current rate limit status."""

    remaining: int
    reset: datetime
    limit: int
    used: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Standard success response."""

    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    size: int = 10
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
