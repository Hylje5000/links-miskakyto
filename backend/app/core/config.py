"""
Simple application configuration.
"""
import os
from typing import List, Optional
from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseSettings(BaseModel):
    """Simple database configuration."""
    url: str = "sqlite:///./links.db"


class SecuritySettings(BaseModel):
    """Simple security configuration."""
    allowed_origins: List[str] = ["http://localhost:3000"]


class LoggingSettings(BaseModel):
    """Simple logging configuration."""
    level: str = "INFO"


class Settings(BaseModel):
    """Simple application settings."""
    
    # App settings
    app_name: str = "Link Shortener API"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    test_mode: bool = False
    
    # API settings
    base_url: str = "http://localhost:8000"
    docs_enabled: bool = True
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    
    def __init__(self, **kwargs):
        # Simple environment variable loading
        super().__init__(
            app_name=os.getenv("APP_NAME", "Link Shortener API"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            test_mode=os.getenv("TEST_MODE", "false").lower() == "true",
            base_url=os.getenv("BASE_URL", "http://localhost:8000"),
            docs_enabled=os.getenv("DOCS_ENABLED", "true").lower() == "true",
            database=DatabaseSettings(
                url=os.getenv("DATABASE_URL", "sqlite:///./links.db")
            ),
            security=SecuritySettings(
                allowed_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
            ),
            logging=LoggingSettings(
                level=os.getenv("LOG_LEVEL", "INFO")
            ),
            **kwargs
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
