"""
Simple Pydantic models for Link Shortener API.
"""
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Union
from datetime import datetime


class LinkCreate(BaseModel):
    """Model for creating a new link."""
    original_url: str
    description: Optional[str] = None
    custom_short_code: Optional[str] = None


class LinkUpdate(BaseModel):
    """Model for updating a link."""
    description: Optional[str] = None


class LinkResponse(BaseModel):
    """Model for link response."""
    id: str
    original_url: str
    short_code: str
    short_url: str
    description: Optional[str] = None
    click_count: int = 0
    created_at: datetime
    created_by: str
    created_by_name: Optional[str] = None
    tenant_id: str


class ClickResponse(BaseModel):
    """Model for click tracking response."""
    id: str
    link_id: str
    clicked_at: datetime
    ip_address: str
    user_agent: Optional[str] = None
    
    @field_validator('id', 'link_id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        """Convert integer IDs to strings."""
        return str(v)


class AnalyticsResponse(BaseModel):
    """Model for analytics response."""
    link_id: str
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    recent_clicks: List[ClickResponse] = []


class LinkListResponse(BaseModel):
    """Model for list of links response."""
    links: List[LinkResponse]
    total: int


class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: str
    version: str
    environment: str
    services: dict = {}
    system: dict = {}
