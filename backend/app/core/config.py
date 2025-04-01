import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Module Creator"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        case_sensitive = True

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./educational_content.db")

    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB in bytes

    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Agent settings
    DOCUMENT_ANALYZER_CONFIG: dict = {
        "name": "document_analyzer",
        "description": "Analyzes educational documents and creates structured outlines",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "prompt_template": """You are an expert educational content analyzer. Your task is to analyze the provided document and create a detailed outline of its content.
        The outline should be structured in a way that makes it easy to understand the main topics and subtopics.
        Please provide a clear hierarchy of information with appropriate headings and subheadings.""",
        "output_format": "json",
        "required_fields": ["title", "sections", "learning_objectives", "key_concepts"],
        "validation_rules": {
            "min_sections": 3,
            "max_sections": 10,
            "min_learning_objectives": 2,
            "max_learning_objectives": 5,
        },
    }


settings = Settings()
