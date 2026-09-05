import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "JobFusion AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = "jobfusion-super-secret-development-key-32chars"
    JWT_SECRET: str = "jobfusion-jwt-secret-token-key-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "jobfusion"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    from pydantic import field_validator
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return [str(i).strip() for i in v]
        return v

    # AI / LLM settings
    LLM_PROVIDER: str = "local"  # "local", "gemini", "ollama"
    LLM_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "tfidf_local"

    # Default Admin
    ADMIN_NAME: str = "Admin Officer"
    ADMIN_EMAIL: str = "admin@jobfusion.ai"
    ADMIN_PASSWORD: str = "AdminPassword123!"

    # File uploads
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_RESUME_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]

    # Ingestion limits
    DISCOVERY_MAX_JOBS_PER_SOURCE: int = 50

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()
