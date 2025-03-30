"""System-related schema definitions."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryUsage(BaseModel):
    """Memory usage statistics."""

    total: int
    used: int
    free: int
    percent: float


class DiskUsage(BaseModel):
    """Disk usage statistics."""

    total: int
    used: int
    free: int
    percent: float


class NetworkStats(BaseModel):
    """Network statistics."""

    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class SystemStats(BaseModel):
    """System statistics model."""

    cpu_usage: float
    memory_usage: MemoryUsage
    disk_usage: DiskUsage
    network_stats: NetworkStats
    process_count: int
    token_usage: int
    estimated_cost: float


class ModelSettings(BaseModel):
    """AI model settings."""

    model_name: str
    api_key: Optional[str] = None  # Optional for Ollama
    max_tokens: int = Field(ge=1)
    temperature: float = Field(ge=0, le=2)
    is_active: bool = True
    cost_per_token: float = Field(ge=0)
    provider: str = "openai"  # 'openai' or 'ollama'
    base_url: Optional[str] = "http://localhost:11434"  # For Ollama server URL

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "gpt-4",
                "api_key": "sk-...",
                "max_tokens": 2000,
                "temperature": 0.7,
                "is_active": True,
                "cost_per_token": 0.03,
                "provider": "openai",
            }
        }


class TokenUsage(BaseModel):
    """Token usage statistics."""

    total_tokens: int
    total_cost: float
    last_reset: str


class AgentContext(BaseModel):
    """Custom context for an agent."""

    context: str
    priority: int = 0
    is_active: bool = True


class Agent(BaseModel):
    """Agent configuration."""

    name: str
    description: str
    role: str
    contexts: List[AgentContext] = []
    is_active: bool = True
    last_active: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "idle"

    class Config:
        frozen = True  # Make the model immutable except for contexts


# Predefined agents for the application
PREDEFINED_AGENTS = [
    Agent(
        name="Document Analyzer",
        description="Analyzes uploaded documents to extract key information, identify topics, and assess content complexity. This agent processes PDF and DOCX files to understand the structure and content of educational materials.",
        role="document_analysis",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
    Agent(
        name="Module Planner",
        description="Designs the learning module structure by organizing content chunks, optimizing learning paths, and identifying prerequisites. This agent creates a logical flow for the educational content.",
        role="module_planning",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
    Agent(
        name="Content Generator",
        description="Creates the actual learning content by writing explanations, generating examples, suggesting visual content, and designing interactive elements. This agent transforms raw content into engaging educational materials.",
        role="content_generation",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
    Agent(
        name="Quiz Generator",
        description="Creates assessments and quizzes by generating questions, validating answers, creating explanations, and calibrating difficulty levels. This agent ensures the learning objectives are properly tested.",
        role="quiz_generation",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
    Agent(
        name="Interactive Content",
        description="Enhances content with interactive elements by selecting UI components, optimizing user experience, and implementing responsive design. This agent makes the learning experience engaging and accessible.",
        role="interactive_content",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
    Agent(
        name="Quality Assurance",
        description="Validates content quality, adds quality metrics, creates feedback systems, and provides improvement suggestions. This agent ensures the educational content meets high standards.",
        role="quality_assurance",
        contexts=[],
        is_active=True,
        last_active=datetime.now().isoformat(),
        status="idle",
    ),
]
