"""
Pydantic models for Link Shortener API.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LinkCreate(BaseModel):
    """Model for creating a new link."""
    original_url: str
    custom_short_code: Optional[str] = None
    description: Optional[str] = None


class LinkUpdate(BaseModel):
    """Model for updating a link."""
    description: Optional[str] = None


class LinkResponse(BaseModel):
    """Model for link response."""
    id: str
    original_url: str
    short_code: str
    short_url: str
    description: Optional[str]
    click_count: int
    created_at: datetime
    created_by: str
    created_by_name: str
    tenant_id: str


class AnalyticsResponse(BaseModel):
    """Model for analytics response."""
    link_id: str
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    recent_clicks: List[dict]


class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: str
    version: str
