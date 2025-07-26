"""
Link Shortener API - Simple and Reliable
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Simple configuration
class Settings:
    app_name = "Link Shortener API"
    version = "1.0.0"
    debug = os.getenv("DEBUG", "false").lower() == "true"
    docs_enabled = True
    base_url = os.getenv("BASE_URL", "http://localhost:3000")
    environment = os.getenv("ENVIRONMENT", "development")

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple application startup and shutdown."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    
    try:
        # Initialize database
        from app.core.database import init_db
        await init_db()
        logger.info("✅ Database initialized")
        logger.info("🎉 Application started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}", exc_info=True)
        raise
    finally:
        logger.info("👋 Application shutdown complete")

def create_app(enable_lifespan=True):
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="A simple URL shortener with Microsoft Entra ID authentication",
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan if enable_lifespan else None
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Include routers
    from app.api import links_router, system_router, redirect_router
    app.include_router(system_router, tags=["System"])
    app.include_router(links_router, tags=["Links"])
    app.include_router(redirect_router, tags=["Redirects"])

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=settings.debug
    )
