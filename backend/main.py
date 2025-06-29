"""
Link Shortener API - Clean Architecture Implementation

This is the main FastAPI application file that orchestrates all components
following clean architecture principles with proper separation of concerns.

Architecture:
- app/core/: Configuration, database, and dependencies
- app/models/: Pydantic models and schemas  
- app/services/: Business logic layer
- app/api/: API route handlers

Features:
- Microsoft Entra ID authentication
- URL shortening with analytics
- Tenant-based access control  
- Clean, testable, modular design
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import links_router, system_router, redirect_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(system_router)  # Root and debug routes - no prefix  
app.include_router(links_router)   # API routes with /api/links prefix
app.include_router(redirect_router)  # Redirect routes - no prefix (short codes)

# Add health endpoint to the /api prefix
@app.get("/api/health")
async def api_health_check():
    """Health check endpoint at /api/health."""
    from app.models.schemas import HealthResponse
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.version
    )


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    logger.info(f"🧪 Test mode: {settings.test_mode}")
    logger.info(f"🔗 Base URL: {settings.base_url}")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
