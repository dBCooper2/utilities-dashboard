import secrets
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Energy Market Dashboard"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # CORS configuration
    CORS_ORIGINS: Optional[List[str]] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        try:
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, list):
                return v
            elif v is None:
                logger.warning("No CORS_ORIGINS provided, defaulting to localhost:3000")
                return ["http://localhost:3000"]
            return []
        except Exception as e:
            logger.error(f"Error parsing CORS_ORIGINS: {e}")
            logger.warning("Using default CORS settings (localhost:3000)")
            return ["http://localhost:3000"]
    
    # Database settings
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    DATABASE_URI: Optional[str] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        try:
            return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
        except Exception as e:
            logger.error(f"Error assembling database URI: {e}")
            return f"postgresql://postgres:postgres@postgres/app"
    
    # API Keys
    RAPID_API_KEY: Optional[str] = "dummy_key"
    EIA_API_KEY: Optional[str] = "dummy_key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Create settings instance
settings = Settings()

# Log configuration on startup
def log_settings():
    logger.info(f"Project: {settings.PROJECT_NAME}")
    logger.info(f"API path: {settings.API_V1_STR}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    logger.info(f"Database: {settings.DATABASE_URI.replace(settings.POSTGRES_PASSWORD, '****')}")
    logger.info(f"API keys configured: {bool(settings.EIA_API_KEY != 'dummy_key')}") 