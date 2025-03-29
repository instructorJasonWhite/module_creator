import json
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Module Creator"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str]

    # File Storage
    UPLOAD_DIR: str
    ALLOWED_FILE_TYPES: List[str]
    MAX_FILE_SIZE: int

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_BURST: int = 200

    # Static Files
    STATIC_DIR: str

    class Config:
        case_sensitive = True
        env_file = ".env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name in ["BACKEND_CORS_ORIGINS", "ALLOWED_FILE_TYPES"]:
                return json.loads(raw_val)
            return raw_val


settings = Settings()
