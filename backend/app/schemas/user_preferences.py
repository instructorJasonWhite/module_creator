from typing import List, Optional

from pydantic import BaseModel


class ModulePreferences(BaseModel):
    module_index: int
    format: str  # 'tabs', 'accordions', 'flashcards', 'video', 'text'
    include_quiz: bool = True
    quiz_type: Optional[str] = None  # 'multiple_choice', 'true_false', 'short_answer'
    include_knowledge_check: bool = True
    knowledge_check_type: Optional[
        str
    ] = None  # 'short_answer', 'matching', 'fill_in_blank'
    settings: Optional[dict] = None


class ModulePreferencesCreate(ModulePreferences):
    pass


class ModulePreferencesUpdate(ModulePreferences):
    pass


class UserPreferencesBase(BaseModel):
    number_of_modules: int = 5
    theme_prompt: Optional[str] = None
    module_preferences: List[ModulePreferences] = []


class UserPreferencesCreate(UserPreferencesBase):
    user_id: int


class UserPreferencesUpdate(UserPreferencesBase):
    pass


class UserPreferencesInDB(UserPreferencesBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
