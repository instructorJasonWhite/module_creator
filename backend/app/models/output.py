from datetime import datetime

from app.db.base_class import Base  # Updated import
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class Output(Base):
    """Output model for generated HTML files."""

    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    html_content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))  # Added relationship
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)

    owner = relationship("User", back_populates="outputs")
    document = relationship(
        "Document"
    )  # Assuming one-to-one or many-to-one with Document
