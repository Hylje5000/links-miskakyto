"""
Link management service.
"""
import shortuuid
import validators
from typing import Optional, Dict, Any, List
from fastapi import HTTPException

from app.core.database import DatabaseManager
from app.core.config import settings
from app.models.schemas import LinkCreate, LinkUpdate, LinkResponse, AnalyticsResponse


class LinkService:
    """Service for managing links."""
    
    @staticmethod
    def generate_short_code() -> str:
        """Generate a unique short code."""
        return shortuuid.uuid()[:8]
    
    @staticmethod
    async def create_link(
        link_data: LinkCreate, 
        user: Dict[str, Any]
    ) -> LinkResponse:
        """Create a new shortened link."""
        # Validate URL
        if not validators.url(link_data.original_url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Generate or validate custom short code
        if link_data.custom_short_code:
            short_code = link_data.custom_short_code
            # Check if custom short code already exists
            existing_link = await DatabaseManager.get_link_by_short_code(short_code)
            if existing_link:
                raise HTTPException(status_code=400, detail="Short code already exists")
        else:
            # Generate unique short code
            while True:
                short_code = LinkService.generate_short_code()
                existing_link = await DatabaseManager.get_link_by_short_code(short_code)
                if not existing_link:
                    break
        
        # Create link
        link_id = shortuuid.uuid()
        await DatabaseManager.create_link(
            link_id=link_id,
            original_url=link_data.original_url,
            short_code=short_code,
            description=link_data.description,
            created_by=user["oid"],
            created_by_name=user.get("name", "Unknown User"),
            tenant_id=user["tid"]
        )
        
        # Return response
        from datetime import datetime, timezone
        return LinkResponse(
            id=link_id,
            original_url=link_data.original_url,
            short_code=short_code,
            short_url=f"{settings.base_url}/{short_code}",
            description=link_data.description,
            click_count=0,
            created_at=datetime.now(timezone.utc),
            created_by=user["oid"],
            created_by_name=user.get("name", "Unknown User"),
            tenant_id=user["tid"]
        )
    
    @staticmethod
    async def get_links_for_tenant(tenant_id: str) -> List[LinkResponse]:
        """Get all links for a tenant."""
        links = await DatabaseManager.get_links_by_tenant(tenant_id)
        
        return [
            LinkResponse(
                id=link["id"],
                original_url=link["original_url"],
                short_code=link["short_code"],
                short_url=f"{settings.base_url}/{link['short_code']}",
                description=link["description"],
                click_count=link["click_count"],
                created_at=link["created_at"],
                created_by=link["created_by"],
                created_by_name=link["created_by_name"],
                tenant_id=link["tenant_id"]
            )
            for link in links
        ]
    
    @staticmethod
    async def get_link(link_id: str, tenant_id: str) -> LinkResponse:
        """Get a specific link by ID."""
        link = await DatabaseManager.get_link_by_id(link_id)
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        if link["tenant_id"] != tenant_id:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return LinkResponse(
            id=link["id"],
            original_url=link["original_url"],
            short_code=link["short_code"],
            short_url=f"{settings.base_url}/{link['short_code']}",
            description=link["description"],
            click_count=link["click_count"],
            created_at=link["created_at"],
            created_by=link["created_by"],
            created_by_name=link["created_by_name"],
            tenant_id=link["tenant_id"]
        )
    
    @staticmethod
    async def update_link(
        link_id: str, 
        link_update: LinkUpdate, 
        tenant_id: str
    ) -> LinkResponse:
        """Update a link."""
        # Check if link exists and belongs to tenant
        existing_link = await DatabaseManager.get_link_by_id(link_id)
        if not existing_link or existing_link["tenant_id"] != tenant_id:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Update link
        updated_link = await DatabaseManager.update_link(link_id, link_update.description)
        
        if not updated_link:
            raise HTTPException(status_code=500, detail="Failed to update link")
        
        return LinkResponse(
            id=updated_link["id"],
            original_url=updated_link["original_url"],
            short_code=updated_link["short_code"],
            short_url=f"{settings.base_url}/{updated_link['short_code']}",
            description=updated_link["description"],
            click_count=updated_link["click_count"],
            created_at=updated_link["created_at"],
            created_by=updated_link["created_by"],
            created_by_name=updated_link["created_by_name"],
            tenant_id=updated_link["tenant_id"]
        )
    
    @staticmethod
    async def delete_link(link_id: str, tenant_id: str) -> None:
        """Delete a link."""
        # Check if link exists and belongs to tenant
        existing_link = await DatabaseManager.get_link_by_id(link_id)
        if not existing_link or existing_link["tenant_id"] != tenant_id:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Delete link
        success = await DatabaseManager.delete_link(link_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete link")
    
    @staticmethod
    async def get_link_analytics(link_id: str, tenant_id: str) -> AnalyticsResponse:
        """Get analytics for a link."""
        # Check if link exists and belongs to tenant
        existing_link = await DatabaseManager.get_link_by_id(link_id)
        if not existing_link or existing_link["tenant_id"] != tenant_id:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Get analytics
        analytics = await DatabaseManager.get_link_analytics(link_id)
        
        return AnalyticsResponse(
            link_id=link_id,
            total_clicks=analytics["total_clicks"],
            clicks_today=analytics["clicks_today"],
            clicks_this_week=analytics["clicks_this_week"],
            clicks_this_month=analytics["clicks_this_month"],
            recent_clicks=analytics["recent_clicks"]
        )
    
    @staticmethod
    async def redirect_to_original(short_code: str, ip_address: str, user_agent: str) -> str:
        """Handle redirection and track clicks."""
        link = await DatabaseManager.get_link_by_short_code(short_code)
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Increment click count
        await DatabaseManager.increment_click_count(link["id"], ip_address, user_agent)
        
        return link["original_url"]
