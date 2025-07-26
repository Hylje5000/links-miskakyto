"""
Simple authentication dependencies.
"""
import os
from typing import Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)  # Don't auto-error so we can handle it ourselves

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """
    Simple token verification for testing and development.
    In production, this should validate JWT tokens from Microsoft Entra ID.
    """
    # In test mode, return a mock user even without credentials
    if os.getenv("TEST_MODE") == "true":
        return {
            "oid": "test-user-id",
            "name": "Test User",
            "tid": "test-tenant-id",
            "email": "test@example.com"
        }
    
    # For now, just validate that a token is present
    # In production, implement proper JWT validation here
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user for development (replace with real JWT validation)
    return {
        "oid": "dev-user-id",
        "name": "Development User",
        "tid": "dev-tenant-id",
        "email": "dev@example.com"
    }
