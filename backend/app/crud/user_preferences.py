import logging
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.user_preferences import ModulePreferences, UserPreferences
from app.schemas.user_preferences import (ModulePreferencesCreate,
                                          ModulePreferencesUpdate,
                                          UserPreferencesCreate,
                                          UserPreferencesUpdate)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CRUDUserPreferences(
    CRUDBase[UserPreferences, UserPreferencesCreate, UserPreferencesUpdate]
):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences by user ID"""
        logger.debug(f"Getting preferences for user {user_id}")
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def create_or_update(
        self, db: Session, *, obj_in: UserPreferencesCreate
    ) -> UserPreferences:
        """Create or update user preferences with module preferences"""
        logger.debug(f"Creating/updating preferences for user {obj_in.user_id}")

        # Get existing preferences
        existing = self.get_by_user_id(db, user_id=obj_in.user_id)

        # Convert input to dict for processing
        obj_in_data = obj_in.model_dump()
        module_preferences = obj_in_data.pop("module_preferences", [])

        if existing:
            logger.debug(f"Updating existing preferences for user {obj_in.user_id}")
            # Update existing preferences
            for field, value in obj_in_data.items():
                setattr(existing, field, value)

            # Clear existing module preferences
            db.query(ModulePreferences).filter(
                ModulePreferences.user_preferences_id == existing.id
            ).delete()

            # Add new module preferences
            for module_pref in module_preferences:
                module_pref_data = module_pref.copy()
                module_pref_data["user_preferences_id"] = existing.id
                db_module_pref = ModulePreferences(**module_pref_data)
                db.add(db_module_pref)

            db.commit()
            db.refresh(existing)
            logger.info(f"Updated preferences for user {obj_in.user_id}")
            return existing
        else:
            logger.debug(f"Creating new preferences for user {obj_in.user_id}")
            # Create new preferences
            db_obj = UserPreferences(**obj_in_data)
            db.add(db_obj)
            db.flush()  # Get the ID of the new preferences

            # Add module preferences
            for module_pref in module_preferences:
                module_pref_data = module_pref.copy()
                module_pref_data["user_preferences_id"] = db_obj.id
                db_module_pref = ModulePreferences(**module_pref_data)
                db.add(db_module_pref)

            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created new preferences for user {obj_in.user_id}")
            return db_obj


crud_user_preferences = CRUDUserPreferences(UserPreferences)
