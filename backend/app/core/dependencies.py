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
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Token validation failed: {error_msg}")
        
        # Provide helpful error messages
        if "Microsoft Graph access token" in error_msg:
            raise HTTPException(
                status_code=401, 
                detail="Invalid token type: Frontend is sending access token instead of ID token. Please use ID token for authentication."
            )
        elif "invalid audience" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid token audience: Token is not intended for this application."
            )
        elif "expired" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Token has expired. Please log in again."
            )
        else:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {error_msg}"
            )


def get_current_user() -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    """
    return Depends(verify_token)
