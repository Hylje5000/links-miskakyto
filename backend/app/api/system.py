"""
Debug and health check routes.
"""
from fastapi import APIRouter, Depends
from datetime import datetime
import os

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


@router.get("/debug/auth-check")
async def debug_auth_check():
    """Debug endpoint to check authentication configuration."""
    return {
        "test_mode": settings.test_mode,
        "azure_tenant_id_set": bool(settings.azure_tenant_id),
        "azure_client_id_set": bool(settings.azure_client_id),
        "base_url": settings.base_url,
        "allowed_origins": settings.allowed_origins,
        "environment_check": {
            "AZURE_TENANT_ID": bool(os.getenv("AZURE_TENANT_ID")),
            "AZURE_CLIENT_ID": bool(os.getenv("AZURE_CLIENT_ID")),
            "TEST_MODE": os.getenv("TEST_MODE", "not_set"),
            "PRODUCTION": os.getenv("PRODUCTION", "not_set")
        }
    }


@router.post("/debug/analyze-token")
async def debug_analyze_token(request_data: dict):
    """Debug endpoint to analyze what token is being sent."""
    token = request_data.get("token")
    if not token:
        return {
            "error": "No token provided",
            "message": "Please provide a token in the request body"
        }
    
    try:
        import jwt
        import json
        
        # Decode without verification to see what's in it
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        unverified_header = jwt.get_unverified_header(token)
        
        # Check what type of token this is
        token_type = "unknown"
        audience = unverified_payload.get("aud", "")
        
        if audience == "00000003-0000-0000-c000-000000000000":
            token_type = "Microsoft Graph Access Token"
        elif audience == settings.azure_client_id:
            token_type = "ID Token (correct)"
        else:
            token_type = f"Unknown token (audience: {audience})"
        
        return {
            "token_type": token_type,
            "expected_audience": settings.azure_client_id,
            "actual_audience": audience,
            "header": unverified_header,
            "claims": {
                "iss": unverified_payload.get("iss"),
                "aud": unverified_payload.get("aud"),
                "exp": unverified_payload.get("exp"),
                "iat": unverified_payload.get("iat"),
                "oid": unverified_payload.get("oid"),
                "name": unverified_payload.get("name"),
                "email": unverified_payload.get("email"),
                "upn": unverified_payload.get("upn"),
                "tid": unverified_payload.get("tid"),
                "idtyp": unverified_payload.get("idtyp"),
                "token_use": unverified_payload.get("token_use"),
            },
            "problem_analysis": {
                "is_access_token": audience == "00000003-0000-0000-c000-000000000000",
                "should_be_id_token": True,
                "frontend_needs_to_use": "ID token instead of access token"
            }
        }
    except Exception as e:
        return {
            "error": f"Failed to decode token: {str(e)}",
            "token_length": len(token),
            "token_preview": token[:50] + "..." if len(token) > 50 else token
        }
