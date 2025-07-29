"""
System health and information routes.
"""
from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {"message": "Link Shortener API", "version": settings.version}


@router.get("/health", response_model=HealthResponse)
@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.version,
        environment=settings.environment
    )
