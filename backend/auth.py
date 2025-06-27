import httpx
import json
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

class AzureADTokenValidator:
    def __init__(self):
        self.jwks_client = PyJWKClient(
            f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"
        )
    
    async def validate_token(self, token: str) -> dict:
        try:
            # Get the signing key
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=AZURE_CLIENT_ID,
                issuer=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"
            )
            
            # Check token expiration
            if datetime.now(timezone.utc).timestamp() > payload.get("exp", 0):
                raise HTTPException(status_code=401, detail="Token has expired")
            
            # Extract user information
            user_data = {
                "oid": payload.get("oid"),  # User object ID
                "name": payload.get("name"),
                "email": payload.get("preferred_username") or payload.get("email"),
                "tid": payload.get("tid", AZURE_TENANT_ID),  # Tenant ID
                "roles": payload.get("roles", []),
                "groups": payload.get("groups", [])
            }
            
            return user_data
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")

# Initialize the validator
token_validator = AzureADTokenValidator()
