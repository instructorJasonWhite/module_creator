from datetime import datetime

from app.db.base_class import Base  # Updated import
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class Document(Base):
    """Document model for uploaded files."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    content_type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analysis = Column(JSON)

    owner = relationship("User", back_populates="documents")
    modules = relationship("Module", back_populates="document")
