from datetime import datetime

from app.db.base_class import Base  # Updated import
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Quiz(Base):
    """Quiz model for module assessments."""

    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    questions = Column(JSON)
    module_id = Column(Integer, ForeignKey("modules.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)

    module = relationship("Module", back_populates="quizzes")
