import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

from ..database.redis_config import get_redis_connection, retry_operation


class AgentConfig(BaseModel):
    """Base configuration model for agents."""

    agent_id: str
    agent_type: str
    enabled: bool = True
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay: int = Field(default=1, ge=1, le=60)
    timeout: int = Field(default=3600, ge=60, le=7200)
    log_level: str = Field(
        default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConfigManager:
    """Manages agent configurations with hot-reloading support."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.redis = get_redis_connection()
        self.logger = logging.getLogger("agent.config")

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables
        load_dotenv()

        # Initialize configuration storage
        self._initialize_config_storage()

    def _initialize_config_storage(self):
        """Initialize configuration storage in Redis."""
        if not self.redis.exists("agent_configs"):
            self.redis.hset(
                "agent_configs",
                mapping={
                    "created_at": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                },
            )

    def load_config(self, agent_type: str) -> Optional[AgentConfig]:
        """
        Load configuration for an agent.
        Args:
            agent_type: Type of agent to load config for
        Returns:
            Optional[AgentConfig]: Agent configuration if found
        """
        # Try to load from Redis first
        config_data = self.redis.hget(f"agent_config:{agent_type}", "config")
        if config_data:
            return AgentConfig.parse_raw(config_data)

        # If not in Redis, try to load from file
        config_file = self.config_dir / f"{agent_type.lower()}.yaml"
        if config_file.exists():
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
                config = AgentConfig(**config_data)
                self._save_config(agent_type, config)
                return config

        # If no config found, create default
        default_config = AgentConfig(
            agent_id=f"{agent_type.lower()}_{datetime.utcnow().timestamp()}",
            agent_type=agent_type,
        )
        self._save_config(agent_type, default_config)
        return default_config

    @retry_operation
    def _save_config(self, agent_type: str, config: AgentConfig):
        """Save configuration to Redis and file."""
        # Save to Redis
        self.redis.hset(
            f"agent_config:{agent_type}",
            mapping={
                "config": config.json(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        # Save to file
        config_file = self.config_dir / f"{agent_type.lower()}.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config.dict(), f)

        # Update last_updated timestamp
        self.redis.hset("agent_configs", "last_updated", datetime.utcnow().isoformat())

    def update_config(self, agent_type: str, updates: Dict[str, Any]) -> AgentConfig:
        """
        Update configuration for an agent.
        Args:
            agent_type: Type of agent to update config for
            updates: Configuration updates
        Returns:
            AgentConfig: Updated configuration
        """
        current_config = self.load_config(agent_type)
        if not current_config:
            raise ValueError(f"No configuration found for agent type: {agent_type}")

        # Update configuration
        updated_config = current_config.copy(update=updates)
        updated_config.updated_at = datetime.utcnow()

        # Save updated configuration
        self._save_config(agent_type, updated_config)

        # Notify agents of configuration change
        self._notify_config_change(agent_type, updated_config)

        return updated_config

    def _notify_config_change(self, agent_type: str, config: AgentConfig):
        """Notify agents of configuration changes."""
        self.redis.publish(
            f"config_change:{agent_type}",
            json.dumps(
                {
                    "agent_type": agent_type,
                    "config": config.json(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
        )

    def get_all_configs(self) -> Dict[str, AgentConfig]:
        """Get all agent configurations."""
        configs = {}
        for key in self.redis.keys("agent_config:*"):
            agent_type = key.split(":")[1]
            configs[agent_type] = self.load_config(agent_type)
        return configs

    def validate_config(self, config: AgentConfig) -> bool:
        """
        Validate agent configuration.
        Args:
            config: Configuration to validate
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Validate required fields
            if not config.agent_id or not config.agent_type:
                return False

            # Validate numeric fields
            if config.max_retries < 1 or config.max_retries > 10:
                return False
            if config.retry_delay < 1 or config.retry_delay > 60:
                return False
            if config.timeout < 60 or config.timeout > 7200:
                return False

            # Validate log level
            if config.log_level not in [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ]:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Configuration validation error: {str(e)}")
            return False
