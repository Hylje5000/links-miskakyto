import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestAPI:
    """Test the main API endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Link Shortener API"
        assert data["version"] == "1.0.0"

    async def test_create_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a new link."""
        link_data = {
            "original_url": "https://example.com/very-long-url",
            "description": "Test link"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == link_data["original_url"]
        assert data["description"] == link_data["description"]
        assert "short_code" in data
        assert "short_url" in data
        assert data["click_count"] == 0

    async def test_create_link_with_custom_code(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a link with a custom short code."""
        link_data = {
            "original_url": "https://example.com/custom-link",
            "custom_short_code": "custom123",
            "description": "Custom link"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "custom123"

    async def test_create_link_invalid_url(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test creating a link with an invalid URL."""
        link_data = {
            "original_url": "not-a-valid-url",
            "description": "Invalid link"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid URL" in response.json()["detail"]

    async def test_get_links(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test getting all links for a user."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-list",
            "description": "Test list link"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # Now get all links
        response = await async_client.get(
            "/api/links",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(link["description"] == "Test list link" for link in data)

    async def test_get_specific_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test getting a specific link by ID."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/specific-link",
            "description": "Specific link"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        
        # Now get the specific link
        response = await async_client.get(
            f"/api/links/{created_link['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_link["id"]
        assert data["description"] == "Specific link"

    async def test_update_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test updating a link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/update-test",
            "description": "Original description"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        
        # Update the link
        update_data = {
            "description": "Updated description"
        }
        
        response = await async_client.put(
            f"/api/links/{created_link['id']}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    async def test_delete_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test deleting a link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/delete-test",
            "description": "To be deleted"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        
        # Delete the link
        response = await async_client.delete(
            f"/api/links/{created_link['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify the link is gone
        get_response = await async_client.get(
            f"/api/links/{created_link['id']}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    async def test_link_analytics(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test getting link analytics."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/analytics-test",
            "description": "Analytics test link"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        
        # Get analytics
        response = await async_client.get(
            f"/api/links/{created_link['id']}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["link_id"] == created_link["id"]
        assert data["click_count"] == 0
        assert isinstance(data["recent_clicks"], list)

    async def test_redirect_link(self, async_client: AsyncClient, auth_headers: dict, test_db: str):
        """Test redirecting via short code."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/redirect-test",
            "custom_short_code": "redirect123"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # Test redirect
        response = await async_client.get(
            "/redirect123",
            follow_redirects=False
        )
        
        assert response.status_code == 302
        assert response.headers["location"] == "https://example.com/redirect-test"

    async def test_redirect_nonexistent_link(self, async_client: AsyncClient, test_db: str):
        """Test redirecting to a non-existent short code."""
        response = await async_client.get(
            "/nonexistent123",
            follow_redirects=False
        )
        
        assert response.status_code == 404

    async def test_unauthorized_access(self, async_client: AsyncClient, test_db: str):
        """Test accessing protected endpoints without authentication."""
        response = await async_client.get("/api/links")
        assert response.status_code == 403  # Should be unauthorized
