import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./grievances.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-cm-kerala-key-2026-minimum-32-chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")
    MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB

settings = Settings()

# Vercel serverless environment support: write to /tmp if SQLite is used without an external DB
if os.getenv("VERCEL") and settings.DATABASE_URL.startswith("sqlite:///./"):
    settings.DATABASE_URL = "sqlite:////tmp/grievances.db"

# Normalize Postgres URLs for SQLAlchemy (e.g. Neon/Render URL might start with postgres://)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
