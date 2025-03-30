import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from app.schemas.system import ModelSettings, SystemStats, AgentContext

MODEL_SETTINGS_FILE = "model_settings.json"
AGENT_CONTEXTS_FILE = "agent_contexts.json"

def load_model_settings() -> Dict[str, ModelSettings]:
    """Load model settings from file."""
    try:
        if os.path.exists(MODEL_SETTINGS_FILE):
            with open(MODEL_SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return {name: ModelSettings(**settings) for name, settings in data.items()}
        return {}
    except Exception as e:
        raise Exception(f"Failed to load model settings: {str(e)}")

def save_model_settings(settings: Dict[str, ModelSettings]) -> None:
    """Save model settings to file."""
    try:
        with open(MODEL_SETTINGS_FILE, "w") as f:
            json.dump(
                {name: settings.dict() for name, settings in settings.items()},
                f,
                indent=2
            )
    except Exception as e:
        raise Exception(f"Failed to save model settings: {str(e)}")

async def get_model_settings() -> Dict[str, ModelSettings]:
    """Get all model settings."""
    return load_model_settings()

async def update_model_settings(model_name: str, settings: ModelSettings) -> ModelSettings:
    """Update model settings."""
    current_settings = load_model_settings()
    
    # If the model is being activated, deactivate all other models
    if settings.is_active:
        for name, model in current_settings.items():
            if name != model_name:
                model.is_active = False
    
    current_settings[model_name] = settings
    save_model_settings(current_settings)
    return settings

async def delete_model_settings(model_name: str) -> None:
    """Delete model settings."""
    current_settings = load_model_settings()
    if model_name in current_settings:
        del current_settings[model_name]
        save_model_settings(current_settings)

def load_agent_contexts() -> List[AgentContext]:
    """Load agent contexts from file."""
    try:
        if os.path.exists(AGENT_CONTEXTS_FILE):
            with open(AGENT_CONTEXTS_FILE, "r") as f:
                data = json.load(f)
                return [AgentContext(**context) for context in data]
        return []
    except Exception as e:
        raise Exception(f"Failed to load agent contexts: {str(e)}")

def save_agent_contexts(contexts: List[AgentContext]) -> None:
    """Save agent contexts to file."""
    try:
        with open(AGENT_CONTEXTS_FILE, "w") as f:
            json.dump([context.dict() for context in contexts], f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save agent contexts: {str(e)}")

async def get_agent_contexts() -> List[AgentContext]:
    """Get all agent contexts."""
    return load_agent_contexts()

async def update_agent_context(context: AgentContext) -> AgentContext:
    """Update agent context."""
    contexts = load_agent_contexts()
    
    # Find and update existing context
    for i, existing in enumerate(contexts):
        if existing.context_id == context.context_id:
            contexts[i] = context
            save_agent_contexts(contexts)
            return context
    
    # Add new context
    contexts.append(context)
    save_agent_contexts(contexts)
    return context

async def delete_agent_context(context_id: str) -> None:
    """Delete agent context."""
    contexts = load_agent_contexts()
    contexts = [c for c in contexts if c.context_id != context_id]
    save_agent_contexts(contexts)

async def get_system_stats() -> SystemStats:
    """Get system statistics."""
    try:
        import psutil
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent
        }
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        # Get network stats
        net_io = psutil.net_io_counters()
        network_stats = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        # Get process count
        process_count = len(psutil.pids())
        
        # Get token usage (placeholder)
        token_usage = 0
        estimated_cost = 0.0
        
        return SystemStats(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_stats=network_stats,
            process_count=process_count,
            token_usage=token_usage,
            estimated_cost=estimated_cost
        )
    except Exception as e:
        raise Exception(f"Failed to get system stats: {str(e)}") 