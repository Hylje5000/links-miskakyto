"""
Debug and health check routes.
"""
from fastapi import APIRouter, Depends
from datetime import datetime

from app.models.schemas import HealthResponse, DebugResponse
from app.core.config import settings
from app.core.dependencies import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])


@router.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {"message": "Link Shortener API", "version": settings.version}


@router.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all available routes."""
    return {
        "available_routes": [
            "GET / - Root endpoint",
            "GET /api/health - Health check",
            "GET /health - Health check (legacy)",
            "POST /api/links - Create link",
            "GET /api/links - Get all links",
            "GET /api/links/{id} - Get specific link",
            "PUT /api/links/{id} - Update link",
            "DELETE /api/links/{id} - Delete link",
            "GET /api/links/{id}/analytics - Get link analytics",
            "GET /{short_code} - Redirect to original URL"
        ],
        "auth_required": "All /api/* endpoints require Bearer token",
        "test_mode": settings.test_mode
    }


@router.get("/debug/auth")
async def debug_auth():
    """Debug endpoint to test authentication."""
    return {
        "message": "This endpoint requires authentication",
        "instructions": [
            "1. Get your ID token from the frontend",
            "2. Include it in the Authorization header as 'Bearer YOUR_TOKEN'",
            "3. Make a request to this endpoint"
        ]
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.version
    )


@router.post("/debug/validate-token", response_model=DebugResponse)
async def debug_token_validation(token_data: dict):
    """Debug endpoint to test token validation."""
    token = token_data.get("token")
    if not token:
        return DebugResponse(
            success=False,
            message="Token is required",
            data={"error": "No token provided"}
        )
    
    try:
        # Import here to avoid issues
        from auth import token_validator
        
        logger.info(f"🔍 Debug: Validating token (length: {len(token)})")
        logger.info(f"🔍 Debug: Token starts with: {token[:20]}...")
        
        user_data = token_validator.validate_token(token)
        
        return DebugResponse(
            success=True,
            message="Token validation successful",
            data={
                "user_data": user_data,
                "token_length": len(token),
                "token_preview": token[:20] + "..."
            }
        )
    except Exception as e:
        logger.error(f"🔍 Debug: Token validation failed: {e}")
        return DebugResponse(
            success=False,
            message=f"Token validation failed: {str(e)}",
            data={
                "error": str(e),
                "token_length": len(token),
                "token_preview": token[:20] + "..."
            }
        )
