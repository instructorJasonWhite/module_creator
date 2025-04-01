from typing import List, Optional

from app.crud import user_preferences as crud_user_preferences
from app.schemas.user_preferences import ModulePreferences, UserPreferencesInDB
from sqlalchemy.orm import Session


class UserPreferencesService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_preferences(self, user_id: int) -> Optional[UserPreferencesInDB]:
        """Get user preferences by user ID"""
        return crud_user_preferences.get_by_user_id(self.db, user_id=user_id)

    def get_module_preferences(
        self, user_id: int, module_index: int
    ) -> Optional[ModulePreferences]:
        """Get specific module preferences for a user"""
        preferences = self.get_user_preferences(user_id)
        if not preferences or not preferences.module_preferences:
            return None

        for module_pref in preferences.module_preferences:
            if module_pref.module_index == module_index:
                return module_pref
        return None

    def get_default_module_preferences(self, user_id: int) -> ModulePreferences:
        """Get default module preferences for a user"""
        preferences = self.get_user_preferences(user_id)
        if not preferences or not preferences.module_preferences:
            return ModulePreferences(
                module_index=0,
                format="text",
                include_quiz=True,
                quiz_type="multiple_choice",
                include_knowledge_check=True,
                knowledge_check_type="short_answer",
            )
        return preferences.module_preferences[0]

    def get_number_of_modules(self, user_id: int) -> int:
        """Get the number of modules a user prefers"""
        preferences = self.get_user_preferences(user_id)
        return preferences.number_of_modules if preferences else 5

    def get_theme_prompt(self, user_id: int) -> Optional[str]:
        """Get the theme prompt for a user"""
        preferences = self.get_user_preferences(user_id)
        return preferences.theme_prompt if preferences else None
