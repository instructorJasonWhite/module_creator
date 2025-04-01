from datetime import datetime

from app.db.base_class import Base  # Updated import
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")
    outputs = relationship("Output", back_populates="owner")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
