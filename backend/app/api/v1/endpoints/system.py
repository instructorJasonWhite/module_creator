"""System endpoints for monitoring and managing system resources."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import psutil
from app.core.auth import get_current_admin
from app.schemas.system import ModelSettings, SystemStats, TokenUsage
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

# File paths for persistent storage
MODEL_SETTINGS_FILE = "model_settings.json"
TOKEN_USAGE_FILE = "token_usage.json"


def load_model_settings() -> List[ModelSettings]:
    """Load model settings from file."""
    if os.path.exists(MODEL_SETTINGS_FILE):
        with open(MODEL_SETTINGS_FILE, "r") as f:
            return [ModelSettings(**model) for model in json.load(f)]
    return []


def save_model_settings(settings: List[ModelSettings]):
    """Save model settings to file."""
    with open(MODEL_SETTINGS_FILE, "w") as f:
        json.dump([model.dict() for model in settings], f, indent=2)


def load_token_usage() -> TokenUsage:
    """Load token usage statistics from file."""
    if os.path.exists(TOKEN_USAGE_FILE):
        with open(TOKEN_USAGE_FILE, "r") as f:
            data = json.load(f)
            return TokenUsage(**data)
    return TokenUsage(
        total_tokens=0, total_cost=0.0, last_reset=datetime.now().isoformat()
    )


def save_token_usage(usage: TokenUsage):
    """Save token usage statistics to file."""
    with open(TOKEN_USAGE_FILE, "w") as f:
        json.dump(usage.dict(), f, indent=2)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(current_admin: str = Depends(get_current_admin)):
    """Get current system statistics."""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
        }

        # Get disk usage
        disk = psutil.disk_usage("/")
        disk_usage = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

        # Get network stats
        net_io = psutil.net_io_counters()
        network_stats = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

        # Get process count
        process_count = len(psutil.pids())

        # Get token usage
        token_usage = load_token_usage()

        return SystemStats(
            cpu_usage=cpu_percent,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_stats=network_stats,
            process_count=process_count,
            token_usage=token_usage.total_tokens,
            estimated_cost=token_usage.total_cost,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelSettings])
async def get_model_settings(current_admin: str = Depends(get_current_admin)):
    """Get all model settings."""
    return load_model_settings()


@router.post("/models", response_model=ModelSettings)
async def create_model_settings(
    model: ModelSettings, current_admin: str = Depends(get_current_admin)
):
    """Create new model settings."""
    settings = load_model_settings()

    # If the new model is being activated, deactivate all other models
    if model.is_active:
        for m in settings:
            m.is_active = False

    settings.append(model)
    save_model_settings(settings)
    return model


@router.put("/models/{model_name}", response_model=ModelSettings)
async def update_model_settings(
    model_name: str,
    model: ModelSettings,
    current_admin: str = Depends(get_current_admin),
):
    """Update existing model settings."""
    settings = load_model_settings()

    # If the model is being activated, deactivate all other models
    if model.is_active:
        for m in settings:
            if m.model_name != model_name:  # Don't deactivate the current model
                m.is_active = False

    for i, m in enumerate(settings):
        if m.model_name == model_name:
            settings[i] = model
            save_model_settings(settings)
            return model
    raise HTTPException(status_code=404, detail="Model not found")


@router.delete("/models/{model_name}")
async def delete_model_settings(
    model_name: str, current_admin: str = Depends(get_current_admin)
):
    """Delete model settings."""
    settings = load_model_settings()
    settings = [m for m in settings if m.model_name != model_name]
    save_model_settings(settings)
    return {"message": "Model deleted successfully"}


@router.get("/token-usage", response_model=TokenUsage)
async def get_token_usage(current_admin: str = Depends(get_current_admin)):
    """Get token usage statistics."""
    return load_token_usage()


@router.post("/token-usage/reset")
async def reset_token_usage(current_admin: str = Depends(get_current_admin)):
    """Reset token usage statistics."""
    usage = TokenUsage(
        total_tokens=0, total_cost=0.0, last_reset=datetime.now().isoformat()
    )
    save_token_usage(usage)
    return usage


@router.get("/agents/status", response_model=Dict[str, Any])
async def get_agent_status(
    current_admin: str = Depends(get_current_admin),
) -> Dict[str, Any]:
    """Get the status of all agents."""
    try:
        # For now, return a mock status
        return {
            "default": {"status": "idle", "last_active": datetime.now().isoformat()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
