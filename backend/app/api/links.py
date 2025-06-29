"""
Link management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends

from app.models.schemas import LinkCreate, LinkUpdate, LinkResponse, AnalyticsResponse
from app.services.link_service import LinkService
from app.core.dependencies import verify_token

router = APIRouter(prefix="/api/links", tags=["links"])


@router.post("", response_model=LinkResponse)
async def create_link(
    link_data: LinkCreate,
    user: dict = Depends(verify_token)
):
    """Create a new shortened link."""
    return await LinkService.create_link(link_data, user)


@router.get("", response_model=List[LinkResponse])
async def get_links(
    user: dict = Depends(verify_token)
):
    """Get all links for the authenticated user's tenant."""
    return await LinkService.get_links_for_tenant(user["tid"])


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: str,
    user: dict = Depends(verify_token)
):
    """Get a specific link by ID."""
    return await LinkService.get_link(link_id, user["tid"])


@router.put("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    link_update: LinkUpdate,
    user: dict = Depends(verify_token)
):
    """Update a link's description."""
    return await LinkService.update_link(link_id, link_update, user["tid"])


@router.delete("/{link_id}")
async def delete_link(
    link_id: str,
    user: dict = Depends(verify_token)
):
    """Delete a link."""
    await LinkService.delete_link(link_id, user["tid"])
    return {"message": "Link deleted successfully"}


@router.get("/{link_id}/analytics", response_model=AnalyticsResponse)
async def get_link_analytics(
    link_id: str,
    user: dict = Depends(verify_token)
):
    """Get analytics for a specific link."""
    return await LinkService.get_link_analytics(link_id, user["tid"])
