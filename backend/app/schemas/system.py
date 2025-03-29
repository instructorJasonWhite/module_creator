"""System-related schema definitions."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


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
    api_key: str
    max_tokens: int
    temperature: float
    is_active: bool = True
    cost_per_token: float = 0.002


class TokenUsage(BaseModel):
    """Token usage statistics."""

    total_tokens: int
    total_cost: float
    last_reset: str
