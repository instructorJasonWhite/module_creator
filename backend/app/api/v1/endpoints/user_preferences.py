import logging
from typing import Any, List

from app.api import deps
from app.crud import user_preferences as crud_user_preferences
from app.schemas.user_preferences import (UserPreferencesCreate,
                                          UserPreferencesInDB,
                                          UserPreferencesUpdate)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserPreferencesInDB)
def get_my_preferences(
    db: Session = Depends(deps.get_db), current_user=Depends(deps.get_current_user)
) -> Any:
    """Get current user's preferences"""
    logger.debug(f"Getting preferences for user {current_user.id}")
    preferences = crud_user_preferences.get_by_user_id(db, user_id=current_user.id)
    if not preferences:
        logger.info(
            f"No preferences found for user {current_user.id}, creating defaults"
        )
        # Create default preferences if none exist
        default_preferences = UserPreferencesCreate(
            user_id=current_user.id,
            number_of_modules=5,
            theme_prompt=None,
            module_preferences=[],
        )
        preferences = crud_user_preferences.create(db, obj_in=default_preferences)
        logger.info(f"Created default preferences for user {current_user.id}")
    return preferences


@router.put("/me", response_model=UserPreferencesInDB)
def update_my_preferences(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
    preferences_in: UserPreferencesUpdate,
) -> Any:
    """Update current user's preferences"""
    logger.debug(f"Updating preferences for user {current_user.id}")
    logger.debug(f"Received preferences: {preferences_in}")

    # Add user_id to the preferences
    preferences_in.user_id = current_user.id

    try:
        # Create or update preferences
        preferences = crud_user_preferences.create_or_update(db, obj_in=preferences_in)
        logger.info(f"Successfully updated preferences for user {current_user.id}")
        return preferences
    except Exception as e:
        logger.error(
            f"Error updating preferences for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to update preferences: {str(e)}"
        )
