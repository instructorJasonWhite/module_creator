"""System endpoints for monitoring and managing system resources."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import psutil
from app.core.auth import get_current_admin
from app.core.security import get_current_user
from app.schemas.system import (PREDEFINED_AGENTS, Agent, AgentContext,
                                ModelSettings, SystemStats, SystemStatus,
                                TokenUsage)
from app.services.system import (delete_agent_context, get_agent_contexts,
                                 get_model_settings, get_system_stats,
                                 update_agent_context, update_model_settings)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

# File paths for persistent storage
MODEL_SETTINGS_FILE = "model_settings.json"
TOKEN_USAGE_FILE = "token_usage.json"
AGENTS_FILE = "agents.json"


def load_model_settings() -> Dict[str, ModelSettings]:
    """Load model settings from file."""
    try:
        if os.path.exists(MODEL_SETTINGS_FILE):
            with open(MODEL_SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Convert list to dictionary using model_name as key
                    return {item["model_name"]: ModelSettings(**item) for item in data}
                elif isinstance(data, dict):
                    # Handle dictionary format
                    return {
                        name: ModelSettings(**settings)
                        for name, settings in data.items()
                    }
                else:
                    logger.error(f"Invalid model settings format: {type(data)}")
                    return {}
        return {}
    except Exception as e:
        logger.error(f"Failed to load model settings: {str(e)}", exc_info=True)
        return {}


def save_model_settings(settings: Dict[str, ModelSettings]):
    """Save model settings to file."""
    with open(MODEL_SETTINGS_FILE, "w") as f:
        json.dump(
            {name: settings.dict() for name, settings in settings.items()}, f, indent=2
        )


def load_token_usage() -> TokenUsage:
    """Load token usage statistics from file."""
    try:
        if os.path.exists(TOKEN_USAGE_FILE):
            with open(TOKEN_USAGE_FILE, "r") as f:
                data = json.load(f)
                # Ensure all required fields are present with defaults
                return TokenUsage(
                    total_tokens=data.get("total_tokens", 0),
                    total_cost=data.get("total_cost", 0.0),
                    last_reset=data.get("last_reset", datetime.now().isoformat()),
                )
    except Exception as e:
        logger.error(f"Failed to load token usage: {str(e)}", exc_info=True)

    # Return default values if file doesn't exist or there's an error
    return TokenUsage(
        total_tokens=0, total_cost=0.0, last_reset=datetime.now().isoformat()
    )


def save_token_usage(usage: TokenUsage):
    """Save token usage statistics to file."""
    with open(TOKEN_USAGE_FILE, "w") as f:
        json.dump(usage.dict(), f, indent=2)


def load_agents() -> List[Agent]:
    """Load agents from file."""
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE, "r") as f:
            return [Agent(**agent) for agent in json.load(f)]
    return []


def save_agents(agents: List[Agent]):
    """Save agents to file."""
    with open(AGENTS_FILE, "w") as f:
        json.dump([agent.dict() for agent in agents], f, indent=2)


@router.get("/agents", response_model=List[Agent])
async def get_agents(current_admin: str = Depends(get_current_admin)):
    """Get all agents."""
    logger.debug(f"Getting agents for admin: {current_admin}")
    agents = load_agents()
    if not agents:  # If no agents exist in file, return predefined agents
        agents = PREDEFINED_AGENTS.copy()  # Make a copy to avoid modifying the original
        save_agents(agents)  # Save predefined agents to file
    logger.debug(f"Retrieved {len(agents)} agents")
    return agents


@router.post("/agents", response_model=Agent)
async def create_agent(agent: Agent, current_admin: str = Depends(get_current_admin)):
    """Create a new agent."""
    logger.debug(f"Creating new agent: {agent.name}")
    agents = load_agents()
    if any(a.name == agent.name for a in agents):
        raise HTTPException(
            status_code=400, detail="Agent with this name already exists"
        )
    agents.append(agent)
    save_agents(agents)
    logger.debug(f"Created agent: {agent.name}")
    return agent


@router.put("/agents/{agent_name}", response_model=Agent)
async def update_agent(
    agent_name: str, agent: Agent, current_admin: str = Depends(get_current_admin)
):
    """Update an existing agent."""
    logger.debug(f"Updating agent: {agent_name}")
    agents = load_agents()
    for i, a in enumerate(agents):
        if a.name == agent_name:
            agents[i] = agent
            save_agents(agents)
            logger.debug(f"Updated agent: {agent_name}")
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@router.delete("/agents/{agent_name}")
async def delete_agent(
    agent_name: str, current_admin: str = Depends(get_current_admin)
):
    """Delete an agent."""
    logger.debug(f"Deleting agent: {agent_name}")
    agents = load_agents()
    agents = [a for a in agents if a.name != agent_name]
    save_agents(agents)
    logger.debug(f"Deleted agent: {agent_name}")
    return {"message": "Agent deleted successfully"}


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(current_admin: str = Depends(get_current_admin)):
    """Get current system statistics."""
    logger.debug(f"Getting system stats for admin: {current_admin}")
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

        logger.debug(
            f"Retrieved system stats: {SystemStats(cpu_usage=cpu_percent, memory_usage=memory_usage, disk_usage=disk_usage, network_stats=network_stats, process_count=process_count, token_usage=token_usage.total_tokens, estimated_cost=token_usage.total_cost).dict()}"
        )
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
        logger.error(f"Failed to get system stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=Dict[str, ModelSettings])
async def read_model_settings(current_user: str = Depends(get_current_user)):
    """Get all model settings."""
    logger.debug(f"Getting model settings for user: {current_user}")
    try:
        models = load_model_settings()
        logger.debug(f"Retrieved {len(models)} model settings")
        return models
    except Exception as e:
        logger.error(f"Failed to get model settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models", response_model=ModelSettings)
async def create_model_settings(
    model_settings: ModelSettings, current_user: str = Depends(get_current_user)
):
    """Create new model settings."""
    logger.debug(f"Creating new model setting for user: {current_user}")
    logger.debug(f"Model settings: {model_settings.dict()}")
    try:
        # Validate provider-specific settings
        if model_settings.provider == "ollama":
            if not model_settings.base_url:
                model_settings.base_url = "http://localhost:11434"
            if model_settings.api_key:
                raise HTTPException(
                    status_code=400,
                    detail="API key is not required for Ollama provider",
                )
        elif model_settings.provider == "openai":
            if not model_settings.api_key:
                raise HTTPException(
                    status_code=400, detail="API key is required for OpenAI provider"
                )
            if model_settings.base_url:
                raise HTTPException(
                    status_code=400,
                    detail="Base URL is not required for OpenAI provider",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {model_settings.provider}",
            )

        updated_model = update_model_settings(model_settings.model_name, model_settings)
        logger.debug(f"Created model setting: {updated_model.dict()}")
        return updated_model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create model setting: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/models/{model_name}", response_model=ModelSettings)
async def update_model_settings_endpoint(
    model_name: str,
    model_settings: ModelSettings,
    current_user: str = Depends(get_current_user),
):
    """Update model settings."""
    logger.debug(f"Updating model settings for model: {model_name}")
    try:
        # Validate provider-specific settings
        if model_settings.provider == "ollama":
            if not model_settings.base_url:
                model_settings.base_url = "http://localhost:11434"
            if model_settings.api_key:
                raise HTTPException(
                    status_code=400,
                    detail="API key is not required for Ollama provider",
                )
        elif model_settings.provider == "openai":
            if not model_settings.api_key:
                raise HTTPException(
                    status_code=400, detail="API key is required for OpenAI provider"
                )
            if model_settings.base_url:
                raise HTTPException(
                    status_code=400,
                    detail="Base URL is not required for OpenAI provider",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {model_settings.provider}",
            )

        updated_model = update_model_settings(model_name, model_settings)
        logger.debug(f"Updated model setting: {updated_model.dict()}")
        return updated_model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model setting: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_name}")
async def delete_model_settings(
    model_name: str, current_user: str = Depends(get_current_user)
):
    """Delete model settings."""
    logger.debug(f"Deleting model settings for model: {model_name}")
    try:
        await delete_model_settings(model_name)
        logger.debug(f"Deleted model settings for model: {model_name}")
        return {"message": "Model settings deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete model settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/token-usage", response_model=TokenUsage)
async def get_token_usage(current_admin: str = Depends(get_current_admin)):
    """Get token usage statistics."""
    logger.debug(f"Getting token usage for admin: {current_admin}")
    return load_token_usage()


@router.post("/token-usage/reset")
async def reset_token_usage(current_admin: str = Depends(get_current_admin)):
    """Reset token usage statistics."""
    logger.debug(f"Resetting token usage for admin: {current_admin}")
    usage = TokenUsage(
        total_tokens=0,
        total_cost=0.0,
        last_reset=datetime.now().isoformat(),
    )
    save_token_usage(usage)
    logger.debug(f"Reset token usage: {usage.dict()}")
    return usage


@router.get("/agents/status", response_model=Dict[str, Any])
async def get_agent_status(
    current_admin: str = Depends(get_current_admin),
) -> Dict[str, Any]:
    """Get the status of all agents."""
    logger.debug(f"Getting agent status for admin: {current_admin}")
    try:
        # For now, return a mock status
        return {
            "default": {"status": "idle", "last_active": datetime.now().isoformat()}
        }
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/contexts", response_model=List[AgentContext])
async def read_agent_contexts(current_user: str = Depends(get_current_user)):
    """Get all agent contexts."""
    logger.debug(f"Getting agent contexts for user: {current_user}")
    try:
        return await get_agent_contexts()
    except Exception as e:
        logger.error(f"Failed to get agent contexts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/contexts", response_model=AgentContext)
async def create_agent_context(
    context: AgentContext, current_user: str = Depends(get_current_user)
):
    """Create new agent context."""
    logger.debug(f"Creating new agent context for user: {current_user}")
    logger.debug(f"Agent context: {context.dict()}")
    try:
        return await update_agent_context(context)
    except Exception as e:
        logger.error(f"Failed to create agent context: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/contexts/{context_id}", response_model=AgentContext)
async def update_agent_context_endpoint(
    context_id: str,
    context: AgentContext,
    current_user: str = Depends(get_current_user),
):
    """Update agent context."""
    logger.debug(f"Updating agent context for context: {context_id}")
    try:
        return await update_agent_context(context)
    except Exception as e:
        logger.error(f"Failed to update agent context: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/contexts/{context_id}")
async def delete_agent_context_endpoint(
    context_id: str, current_user: str = Depends(get_current_user)
):
    """Delete agent context."""
    logger.debug(f"Deleting agent context for context: {context_id}")
    try:
        await delete_agent_context(context_id)
        logger.debug(f"Deleted agent context: {context_id}")
        return {"message": "Agent context deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete agent context: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    try:
        response = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.debug(f"Health check response: {response}")
        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
