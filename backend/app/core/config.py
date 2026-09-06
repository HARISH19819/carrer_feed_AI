import os
from typing import List, Union
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

    # CORS - Union[str, List[str]] prevents pydantic-settings json.loads() crash when set to "*"
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: Union[str, List[str]] = "*"

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            val = self.ALLOWED_ORIGINS.strip()
            if val == "*" or not val:
                return ["*"]
            return [i.strip() for i in val.split(",") if i.strip()]
        elif isinstance(self.ALLOWED_ORIGINS, (list, tuple)):
            return [str(i).strip() for i in self.ALLOWED_ORIGINS]
        return ["*"]

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
