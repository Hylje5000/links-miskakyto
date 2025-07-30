"""
Redirect routes for short codes.
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.services.service import LinkService


def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP address from request headers.
    Checks X-Forwarded-For and X-Real-IP headers set by nginx proxy.
    """
    # Check X-Forwarded-For header (may contain multiple IPs)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip
    
    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP (will be container IP in proxied setups)
    return request.client.host if request.client else "unknown"


router = APIRouter(tags=["redirect"])

# Optional debugging for specific short codes via env var
DEBUG_CODES = {c.strip() for c in os.getenv("DEBUG_REDIRECT_CODES", "").split(",") if c.strip()}


@router.get("/{short_code}")
async def redirect_to_original(short_code: str, request: Request):
    """Redirect to the original URL using the short code."""
    # Debug logging for configured short codes
    if short_code in DEBUG_CODES:
        print(f"🔍 DEBUG: Redirect request for '{short_code}'")
        print(f"🔍 DEBUG: Request URL: {request.url}")
        print(f"🔍 DEBUG: Request path: {request.url.path}")
        print(f"🔍 DEBUG: Headers: {dict(request.headers)}")
    
    # Get client IP and user agent for analytics
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        # Get original URL and track click
        original_url = await LinkService.redirect_to_original(short_code, client_ip, user_agent)
        
        if short_code in DEBUG_CODES:
            print(f"✅ DEBUG: Found '{short_code}' -> {original_url}")
        
        return RedirectResponse(url=original_url, status_code=302)
    except Exception as e:
        if short_code in DEBUG_CODES:
            print(f"❌ DEBUG: Redirect failed for '{short_code}': {e}")
        raise
