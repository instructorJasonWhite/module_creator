from datetime import datetime

from app.db.base_class import Base  # Updated import
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class Module(Base):
    """Module model for generated learning content."""

    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    order = Column(Integer)
    document_id = Column(Integer, ForeignKey("documents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)

    document = relationship("Document", back_populates="modules")
    quizzes = relationship("Quiz", back_populates="module")
