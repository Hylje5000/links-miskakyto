import pytest
from httpx import AsyncClient
import os

class TestRedirectAndHealth:
    """Test redirect functionality and health endpoints."""

    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test the health endpoint."""
        response = await async_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    async def test_redirect_nonexistent_link(self, async_client: AsyncClient, test_db: str):
        """Test redirecting to a non-existent short link."""
        response = await async_client.get("/nonexistent123", follow_redirects=False)
        assert response.status_code == 404

    async def test_redirect_existing_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test redirecting to an existing short link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/redirect-test",
            "description": "Redirect test link"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        created_link = create_response.json()
        short_code = created_link["short_code"]
        
        # Test redirect
        redirect_response = await async_client.get(f"/{short_code}", follow_redirects=False)
        assert redirect_response.status_code == 302
        assert redirect_response.headers["location"] == link_data["original_url"]

class TestLinkValidation:
    """Test link validation and edge cases."""

    async def test_create_link_with_spaces_in_url(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a link with spaces in URL (should be handled)."""
        link_data = {
            "original_url": "https://example.com/path with spaces",
            "description": "URL with spaces test"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        # Should either accept it or return a validation error
        assert response.status_code in [200, 400, 422]

    async def test_create_link_with_unicode_description(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a link with unicode characters in description."""
        link_data = {
            "original_url": "https://example.com/unicode-test",
            "description": "Test with unicode: 🚀 🌟 café naïve"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        created_link = response.json()
        assert created_link["description"] == link_data["description"]

    async def test_create_link_very_long_url(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a link with a very long URL."""
        # Create a very long URL (2000+ characters)
        long_path = "a" * 2000
        link_data = {
            "original_url": f"https://example.com/{long_path}",
            "description": "Very long URL test"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        # Should handle long URLs appropriately
        assert response.status_code in [200, 400]

    async def test_custom_short_code_validation(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test custom short code validation."""
        # Test with special characters
        link_data = {
            "original_url": "https://example.com/special-chars",
            "custom_short_code": "test@#$%",
            "description": "Special chars test"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        # Should validate custom short codes
        assert response.status_code in [200, 422]

class TestAnalytics:
    """Test analytics functionality."""

    async def test_analytics_for_nonexistent_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test getting analytics for a non-existent link."""
        response = await async_client.get(
            "/api/links/nonexistent/analytics",
            headers=auth_headers
        )
        assert response.status_code == 404

    async def test_analytics_empty_clicks(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test analytics for a link with no clicks."""
        # Create a link
        link_data = {
            "original_url": "https://example.com/no-clicks",
            "description": "No clicks test"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        created_link = create_response.json()
        
        # Get analytics
        analytics_response = await async_client.get(
            f"/api/links/{created_link['id']}/analytics",
            headers=auth_headers
        )
        
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert analytics["total_clicks"] == 0
        assert len(analytics["recent_clicks"]) == 0

class TestConcurrency:
    """Test concurrent operations."""

    async def test_concurrent_link_creation_same_custom_code(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating links with the same custom code concurrently."""
        link_data1 = {
            "original_url": "https://example.com/concurrent1",
            "custom_short_code": "concurrent123"
        }
        
        link_data2 = {
            "original_url": "https://example.com/concurrent2",
            "custom_short_code": "concurrent123"
        }
        
        # Create first link
        response1 = await async_client.post("/api/links", json=link_data1, headers=auth_headers)
        
        # Try to create second link with same code
        response2 = await async_client.post("/api/links", json=link_data2, headers=auth_headers)
        
        # One should succeed, one should fail
        assert (response1.status_code == 200 and response2.status_code == 400) or \
               (response1.status_code == 400 and response2.status_code == 200)

class TestLinkLifecycle:
    """Test complete link lifecycle."""

    async def test_complete_link_lifecycle(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating, reading, updating, and deleting a link."""
        # Create
        link_data = {
            "original_url": "https://example.com/lifecycle",
            "description": "Lifecycle test link"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        link_id = created_link["id"]
        
        # Read
        get_response = await async_client.get(
            f"/api/links/{link_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        retrieved_link = get_response.json()
        assert retrieved_link["original_url"] == link_data["original_url"]
        
        # Update
        update_data = {"description": "Updated lifecycle test link"}
        update_response = await async_client.put(
            f"/api/links/{link_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_link = update_response.json()
        assert updated_link["description"] == update_data["description"]
        
        # Delete
        delete_response = await async_client.delete(
            f"/api/links/{link_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        assert "message" in delete_response.json()
        
        # Verify deletion
        get_after_delete = await async_client.get(
            f"/api/links/{link_id}",
            headers=auth_headers
        )
        assert get_after_delete.status_code == 404
