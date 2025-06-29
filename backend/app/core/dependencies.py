"""
FastAPI dependencies for authentication and other common operations.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer(auto_error=not settings.test_mode)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Verify the ID token and return user data.
    
    Returns:
        Dict containing user information from the ID token
    """
    if settings.test_mode:
        # Return mock user data for testing
        logger.info("🧪 Using test mode - returning mock user data")
        return {
            "oid": "test-user-id",
            "name": "Test User",
            "email": "test@example.com",
            "tid": "test-tenant-id"
        }
    
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    logger.info(f"🔑 Validating token (length: {len(token)})")
    
    try:
        # Import here to avoid circular imports and ensure settings are loaded
        from auth import token_validator
        
        user_data = token_validator.validate_token(token)
        logger.info(f"✅ Token validation successful for user: {user_data.get('email', 'unknown')}")
        return user_data
    except HTTPException as e:
        logger.error(f"❌ Token validation failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"💥 Unexpected error during token validation: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


def get_current_user() -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    """
    return Depends(verify_token)
