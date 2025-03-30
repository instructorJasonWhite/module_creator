from dataclasses import dataclass, field
from typing import List
from pydantic import AnyHttpUrl
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    PROJECT_NAME: str = "Module Creator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"  # Change this in production

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./module_creator.db")

    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

settings = Settings()
