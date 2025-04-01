import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

MODEL_SETTINGS_FILE = Path("model_settings.json")


async def get_active_model() -> Optional[Dict[str, Any]]:
    """
    Get the currently active model settings from model_settings.json.

    Returns:
        Optional[Dict[str, Any]]: The active model settings or None if no active model is found
    """
    try:
        logger.debug(
            f"Looking for model settings file at: {MODEL_SETTINGS_FILE.absolute()}"
        )
        if not MODEL_SETTINGS_FILE.exists():
            logger.error(
                f"Model settings file not found at {MODEL_SETTINGS_FILE.absolute()}"
            )
            return None

        with open(MODEL_SETTINGS_FILE, "r") as f:
            models = json.load(f)
            logger.debug(f"Loaded models from settings file: {models}")

        # Find the active model
        active_model = next(
            (model for model in models if model.get("is_active", False)), None
        )

        if not active_model:
            logger.warning("No active model found in settings")
            return None

        logger.info(f"Found active model: {active_model['model_name']}")
        logger.debug(f"Active model settings: {active_model}")
        return active_model

    except Exception as e:
        logger.error(f"Error getting active model: {str(e)}", exc_info=True)
        return None
