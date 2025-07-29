"""
Secure authentication dependencies with Microsoft Entra ID JWT validation.
"""
import os
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Import the secure token validator with error handling
try:
    from auth import token_validator
    TOKEN_VALIDATOR_AVAILABLE = True
    logger.info("✅ Token validator imported successfully")
except ImportError as e:
    TOKEN_VALIDATOR_AVAILABLE = False
    logger.error(f"❌ Failed to import token validator: {e}")
    logger.error("   This will cause authentication to fail in production!")
except Exception as e:
    TOKEN_VALIDATOR_AVAILABLE = False
    logger.error(f"❌ Unexpected error importing token validator: {e}")


async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT tokens from Microsoft Entra ID.
    
    In TEST_MODE only, allows bypassing authentication for testing.
    In production, always validates JWT tokens against Microsoft Entra ID.
    """
    # Only allow test mode bypass if explicitly enabled AND in test environment
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if test_mode:
        logger.warning("⚠️  Running in TEST_MODE - authentication bypassed")
        return {
            "oid": "test-user-id",
            "name": "Test User", 
            "tid": "test-tenant-id",
            "email": "test@example.com"
        }
    
    # Production and development require valid JWT tokens
    if not credentials or not credentials.credentials:
        logger.warning("Authentication failed: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required - valid Microsoft Entra ID token needed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Validate the JWT token against Microsoft Entra ID
        claims = token_validator.validate_token(credentials.credentials)
        
        logger.info(f"✅ Successfully authenticated user: {claims.get('email', claims.get('upn', claims.get('name', 'unknown')))}")
        
        return claims
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
