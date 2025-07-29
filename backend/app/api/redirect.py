"""
Redirect routes for short codes.
"""
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


@router.get("/{short_code}")
async def redirect_to_original(short_code: str, request: Request):
    """Redirect to the original URL using the short code."""
    # Debug logging
    print(f"🔍 Redirect request for short_code: '{short_code}'")
    
    # Get client IP and user agent for analytics
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    print(f"🔍 Client IP: {client_ip}, User Agent: {user_agent[:50]}...")
    
    try:
        # Get original URL and track click
        original_url = await LinkService.redirect_to_original(short_code, client_ip, user_agent)
        print(f"✅ Redirecting '{short_code}' to: {original_url}")
        return RedirectResponse(url=original_url, status_code=302)
    except Exception as e:
        print(f"❌ Redirect failed for '{short_code}': {e}")
        raise
