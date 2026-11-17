import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./grievances.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-cm-kerala-key-2026-minimum-32-chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")
    MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Normalize Postgres URLs for SQLAlchemy (e.g. Neon/Render URL might start with postgres://)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
