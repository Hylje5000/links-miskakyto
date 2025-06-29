"""
Redirect routes for short codes.
"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.services.link_service import LinkService

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
async def redirect_to_original(short_code: str, request: Request):
    """Redirect to the original URL using the short code."""
    # Get client IP and user agent for analytics
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Get original URL and track click
    original_url = await LinkService.redirect_to_original(short_code, client_ip, user_agent)
    
    return RedirectResponse(url=original_url, status_code=302)
