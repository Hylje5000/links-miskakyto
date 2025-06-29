"""
Application configuration and settings.
"""
import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseModel):
    """Application settings."""
    
    # App settings
    app_name: str = "Link Shortener API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Test mode
    test_mode: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # Azure AD settings
    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./links.db")
    
    # API settings
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")


# Global settings instance
settings = Settings()
