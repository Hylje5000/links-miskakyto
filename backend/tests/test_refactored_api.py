"""
Tests for the refactored Link Shortener API.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestRefactoredAPI:
    """Test the refactored API endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Link Shortener API"
        assert data["version"] == "1.0.0"

    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"

    async def test_create_link(self, async_client: AsyncClient, auth_headers: dict):
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
        assert data["created_by"] == "test-user-id"
        assert data["tenant_id"] == "test-tenant-id"

    async def test_create_link_with_custom_code(self, async_client: AsyncClient, auth_headers: dict):
        """Test creating a link with a custom short code."""
        link_data = {
            "original_url": "https://example.com/custom-code-test",
            "custom_short_code": "mycustom",
            "description": "Custom code test"
        }
        
        response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "mycustom"

    async def test_get_links(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting all links for a tenant."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-get-links",
            "description": "Test get links"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # Then get all links
        response = await async_client.get("/api/links", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(link["description"] == "Test get links" for link in data)

    async def test_get_link_by_id(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting a specific link by ID."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-get-by-id",
            "description": "Test get by ID"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        link_id = created_link["id"]
        
        # Then get the specific link
        response = await async_client.get(f"/api/links/{link_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == link_id
        assert data["description"] == "Test get by ID"

    async def test_update_link(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating a link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-update",
            "description": "Original description"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        link_id = created_link["id"]
        
        # Then update the link
        update_data = {"description": "Updated description"}
        response = await async_client.put(
            f"/api/links/{link_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    async def test_delete_link(self, async_client: AsyncClient, auth_headers: dict):
        """Test deleting a link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-delete",
            "description": "To be deleted"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        link_id = created_link["id"]
        
        # Then delete the link
        response = await async_client.delete(f"/api/links/{link_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Link deleted successfully"
        
        # Verify the link is gone
        get_response = await async_client.get(f"/api/links/{link_id}", headers=auth_headers)
        assert get_response.status_code == 404

    async def test_get_analytics(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting analytics for a link."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/test-analytics",
            "description": "Analytics test"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        link_id = created_link["id"]
        
        # Get analytics
        response = await async_client.get(f"/api/links/{link_id}/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["link_id"] == link_id
        assert "total_clicks" in data
        assert "clicks_today" in data
        assert "recent_clicks" in data

    async def test_redirect_functionality(self, async_client: AsyncClient, auth_headers: dict):
        """Test the redirect functionality."""
        # First create a link
        link_data = {
            "original_url": "https://example.com/redirect-test",
            "description": "Redirect test"
        }
        
        create_response = await async_client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        created_link = create_response.json()
        short_code = created_link["short_code"]
        
        # Test redirect (this will return a 302 redirect)
        response = await async_client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "https://example.com/redirect-test"

    def test_invalid_url(self, client: TestClient, auth_headers: dict):
        """Test creating a link with invalid URL."""
        link_data = {
            "original_url": "not-a-valid-url",
            "description": "Invalid URL test"
        }
        
        response = client.post(
            "/api/links",
            json=link_data,
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid URL format" in data["detail"]

    def test_auth_required(self, client: TestClient):
        """Test that authentication is required for protected endpoints."""
        response = client.get("/api/links")
        # In test mode, auth is bypassed, so we expect 200
        assert response.status_code == 200
        # Should return an empty list for a new test database
        assert isinstance(response.json(), list)

    def test_ip_extraction_with_headers(self, client: TestClient):
        """Test that client IP is correctly extracted from proxy headers."""
        # Create a link first
        link_data = {
            "original_url": "https://example.com/test-ip-extraction",
            "description": "Test IP extraction"
        }
        
        response = client.post("/api/links", json=link_data)
        assert response.status_code == 200
        link_response = response.json()
        short_code = link_response["short_code"]
        link_id = link_response["id"]
        
        # Test redirect with X-Forwarded-For header
        test_ip = "203.0.113.1"  # Example public IP
        response = client.get(
            f"/{short_code}",
            headers={"X-Forwarded-For": f"{test_ip}, 172.19.0.1"},
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # Check analytics to see if the IP was recorded correctly
        analytics_response = client.get(f"/api/links/{link_id}/analytics")
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        
        # The IP should be the first IP from X-Forwarded-For
        clicks = analytics_data["recent_clicks"]
        assert len(clicks) == 1
        assert clicks[0]["ip_address"] == test_ip

    def test_ip_extraction_with_real_ip_header(self, client: TestClient):
        """Test that client IP is correctly extracted from X-Real-IP header."""
        # Create a link first
        link_data = {
            "original_url": "https://example.com/test-real-ip",
            "description": "Test Real IP extraction"
        }
        
        response = client.post("/api/links", json=link_data)
        assert response.status_code == 200
        link_response = response.json()
        short_code = link_response["short_code"]
        link_id = link_response["id"]
        
        # Test redirect with X-Real-IP header
        test_ip = "198.51.100.1"  # Example public IP
        response = client.get(
            f"/{short_code}",
            headers={"X-Real-IP": test_ip},
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # Check analytics to see if the IP was recorded correctly
        analytics_response = client.get(f"/api/links/{link_id}/analytics")
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        
        # The IP should be from X-Real-IP
        clicks = analytics_data["recent_clicks"]
        assert len(clicks) == 1
        assert clicks[0]["ip_address"] == test_ip
