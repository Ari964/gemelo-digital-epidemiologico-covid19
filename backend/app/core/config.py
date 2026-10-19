import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
from pydantic import ConfigDict

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel
    class BaseSettings(BaseModel):
        pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "Population-Level Digital Twin"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Storage & Models
    MODELS_DIR: str = os.getenv(
        "MODELS_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
    )
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/epidemic_twin"
    )
    
    # JWT Security & Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_key_population_level_digital_twin_2026_change_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Ollama Local LLM
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
    OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8502",
        "http://127.0.0.1:8502",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    model_config = ConfigDict(case_sensitive=True, extra="allow")

settings = Settings()
