import enum

from app.db.base_class import Base
from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class ModuleFormat(str, enum.Enum):
    TABS = "tabs"
    ACCORDIONS = "accordions"
    FLASHCARDS = "flashcards"
    VIDEO = "video"
    TEXT = "text"


class ModulePreferences(Base):
    """Model for storing module-specific preferences"""

    __tablename__ = "module_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_preferences_id = Column(
        Integer, ForeignKey("user_preferences.id"), nullable=False
    )
    module_index = Column(Integer, nullable=False)  # Position of the module (0-based)

    # Module-specific format
    format = Column(Enum(ModuleFormat), default=ModuleFormat.TABS)

    # Assessment settings
    include_quiz = Column(Boolean, default=True)
    quiz_type = Column(String, nullable=True)  # multiple_choice, true_false, etc.
    include_knowledge_check = Column(Boolean, default=True)
    knowledge_check_type = Column(String, nullable=True)  # short_answer, matching, etc.

    # Additional module-specific settings
    settings = Column(JSON, nullable=True)

    # Relationship with UserPreferences
    user_preferences = relationship(
        "UserPreferences", back_populates="module_preferences"
    )


class UserPreferences(Base):
    """Model for storing user preferences"""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Global settings
    number_of_modules = Column(Integer, default=5)
    theme_prompt = Column(
        String, nullable=True
    )  # Custom theme prompt for HTML generation

    # Additional global settings stored as JSON for flexibility
    additional_settings = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="preferences")
    module_preferences = relationship(
        "ModulePreferences",
        back_populates="user_preferences",
        cascade="all, delete-orphan",
    )
