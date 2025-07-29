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

# Import proper settings
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple application startup and shutdown."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        # Initialize database
        from app.core.database import init_db
        logger.info("🔧 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized successfully")
        logger.info("🎉 Application started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}", exc_info=True)
        # Don't re-raise the exception in production - use fallback instead
        if settings.environment != "production":
            raise
        else:
            logger.error("🚨 Production startup failed - this should trigger container restart")
            # In production, we want the container to restart rather than hang
            import sys
            sys.exit(1)
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
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Include routers - ORDER MATTERS!
    from app.api import links_router, health_router, redirect_router
    
    # API routes first (most specific)
    app.include_router(links_router, tags=["Links"])
    app.include_router(health_router, tags=["Health"])
    
    # Redirect router LAST (catches all remaining /{short_code} routes)
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
