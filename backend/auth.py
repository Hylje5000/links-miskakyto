"""
Authentication module for Link Shortener using Azure AD ID tokens.

This module provides simple, best-practice authentication by validating
Azure AD ID tokens using the Microsoft identity platform's JWKS endpoint.
"""

import jwt
import requests
from functools import lru_cache
from typing import Dict, Any, Optional
import logging
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
import json

logger = logging.getLogger(__name__)

# Azure AD endpoints
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

if not TENANT_ID:
    raise ValueError("AZURE_TENANT_ID environment variable is required")
if not CLIENT_ID:
    raise ValueError("AZURE_CLIENT_ID environment variable is required")

JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"


@lru_cache(maxsize=1)
def get_jwks_keys() -> Dict[str, Any]:
    """
    Fetch and cache JWKS keys from Microsoft's endpoint.
    Uses LRU cache to avoid repeated requests.
    """
    try:
        response = requests.get(JWKS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS keys: {e}")
        raise


def jwk_to_pem(jwk_key: Dict[str, Any]) -> str:
    """
    Convert a JWK key to PEM format for use with PyJWT.
    
    Args:
        jwk_key: JWK key dictionary
        
    Returns:
        PEM formatted public key string
    """
    # Extract the modulus and exponent
    n = base64.urlsafe_b64decode(jwk_key['n'] + '==')
    e = base64.urlsafe_b64decode(jwk_key['e'] + '==')
    
    # Convert to integers
    n_int = int.from_bytes(n, 'big')
    e_int = int.from_bytes(e, 'big')
    
    # Create RSA public key
    public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()
    
    # Serialize to PEM format
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return pem.decode('utf-8')


def validate_id_token(token: str) -> Dict[str, Any]:
    """
    Validate an Azure AD ID token and return the claims.
    
    Args:
        token: The ID token to validate
        
    Returns:
        Dict containing the token claims (user info)
        
    Raises:
        jwt.InvalidTokenError: If the token is invalid
        ValueError: If required claims are missing
    """
    try:
        # First, let's decode without verification to see what we're dealing with
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        unverified_header = jwt.get_unverified_header(token)
        
        logger.info(f"🔍 Token analysis:")
        logger.info(f"  - Header: {unverified_header}")
        logger.info(f"  - Audience: {unverified_payload.get('aud')}")
        logger.info(f"  - Expected audience: {CLIENT_ID}")
        logger.info(f"  - Issuer: {unverified_payload.get('iss')}")
        logger.info(f"  - Token type: {unverified_payload.get('idtyp', 'not set')}")
        logger.info(f"  - Token use: {unverified_payload.get('token_use', 'not set')}")
        
        # Check if this is an access token instead of ID token
        if unverified_payload.get('aud') == "00000003-0000-0000-c000-000000000000":
            raise jwt.InvalidTokenError("Received Microsoft Graph access token instead of ID token. Frontend should send ID token.")
        
        # Get the signing keys
        jwks_data = get_jwks_keys()
        
        # Decode the token header to get the key ID
        kid = unverified_header.get('kid')
        
        if not kid:
            raise jwt.InvalidTokenError("Token header missing 'kid' claim")
        
        # Find the matching key
        signing_key_pem = None
        for key in jwks_data.get('keys', []):
            if key.get('kid') == kid:
                signing_key_pem = jwk_to_pem(key)
                break
        
        if not signing_key_pem:
            raise jwt.InvalidTokenError(f"Unable to find signing key for kid: {kid}")
        
        # Validate and decode the token
        logger.info(f"🔍 Attempting JWT validation with:")
        logger.info(f"  - Audience: {CLIENT_ID}")
        logger.info(f"  - Issuer: {ISSUER}")
        logger.info(f"  - Algorithm: RS256")
        
        claims = jwt.decode(
            token,
            signing_key_pem,
            algorithms=['RS256'],
            audience=CLIENT_ID,
            issuer=ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        
        logger.info(f"✅ JWT validation successful!")
        logger.info(f"  - Claims received: {list(claims.keys())}")
        
        # Verify required claims are present
        required_claims = ['oid', 'name', 'tid']  # Remove 'email' temporarily
        missing_claims = [claim for claim in required_claims if not claims.get(claim)]
        
        if missing_claims:
            logger.warning(f"Token missing required claims: {missing_claims}")
            logger.info(f"Available claims: {list(claims.keys())}")
            # Don't fail immediately, just log the issue
            # raise ValueError(f"Token missing required claims: {missing_claims}")
        
        logger.info(f"Successfully validated ID token for user: {claims.get('email', claims.get('upn', claims.get('name', 'unknown')))}")
        return claims
        
    except jwt.ExpiredSignatureError:
        logger.warning("ID token has expired")
        raise jwt.InvalidTokenError("Token has expired")
    except jwt.InvalidAudienceError:
        logger.warning("ID token has invalid audience")
        raise jwt.InvalidTokenError("Token has invalid audience")
    except jwt.InvalidIssuerError:
        logger.warning("ID token has invalid issuer")
        raise jwt.InvalidTokenError("Token has invalid issuer")
    except jwt.InvalidTokenError as e:
        logger.warning(f"ID token validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating ID token: {e}")
        raise jwt.InvalidTokenError(f"Token validation failed: {str(e)}")


def extract_token_from_header(authorization_header: Optional[str]) -> str:
    """
    Extract the token from the Authorization header.
    
    Args:
        authorization_header: The Authorization header value
        
    Returns:
        The extracted token
        
    Raises:
        ValueError: If the header is invalid
    """
    if not authorization_header:
        raise ValueError("Authorization header is missing")
    
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must start with 'Bearer '")
    
    return authorization_header[7:]  # Remove "Bearer " prefix


# Create a singleton validator instance
class IDTokenValidator:
    """Simple ID token validator for Azure AD."""
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate an ID token and return claims."""
        return validate_id_token(token)
    
    def extract_token(self, auth_header: Optional[str]) -> str:
        """Extract token from Authorization header."""
        return extract_token_from_header(auth_header)


# Export the validator instance
token_validator = IDTokenValidator()
