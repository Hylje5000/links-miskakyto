"""
API package initialization.
"""
from .links import router as links_router
from .health import router as health_router
from .redirect import router as redirect_router

__all__ = ["links_router", "health_router", "redirect_router"]
