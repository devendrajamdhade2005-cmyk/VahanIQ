"""
Application configuration using Pydantic settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AutoSense AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"  # or "openai"
    LLM_MODEL: str = "claude-3-sonnet-20240229"
    
    # ML
    ML_MODEL_PATH: str = "../ml/models/failure_prediction_model.pkl"
    SHAP_EXPLAINER_PATH: str = "../ml/models/shap_explainer.pkl"
    
    # RAG
    RAG_INDEX_PATH: str = "app/rag/indices/faiss_index"
    RAG_EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    RAG_TOP_K_RESULTS: int = 5
    
    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
