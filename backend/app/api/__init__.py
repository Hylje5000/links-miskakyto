"""
API package initialization.
"""
from .links import router as links_router
from .system import router as system_router
from .redirect import router as redirect_router

__all__ = ["links_router", "system_router", "redirect_router"]
