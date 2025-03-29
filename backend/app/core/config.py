from typing import List, Optional

from pydantic import AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Module Creator"
    API_V1_STR: str = "/api/v1"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./module_creator.db"

    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes

    # Admin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"  # Change in production

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")


settings = Settings()
