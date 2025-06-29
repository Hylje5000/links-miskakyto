import pytest
from unittest.mock import Mock, AsyncMock
import os

# Set test mode before importing
os.environ["TEST_MODE"] = "true"
os.environ["AZURE_TENANT_ID"] = "test-tenant"
os.environ["AZURE_CLIENT_ID"] = "test-client"

from app.services.link_service import LinkService
from app.models.schemas import LinkCreate, LinkUpdate
from app.core.database import DatabaseManager


@pytest.mark.unit
class TestLinkService:
    """Unit tests for LinkService."""

    def test_generate_short_code(self):
        """Test short code generation."""
        code = LinkService.generate_short_code()
        assert isinstance(code, str)
        assert len(code) == 8
        
        # Generate multiple codes to ensure they're different
        codes = [LinkService.generate_short_code() for _ in range(10)]
        assert len(set(codes)) == 10  # All should be unique

    @pytest.mark.asyncio
    async def test_create_link_invalid_url(self):
        """Test creating a link with invalid URL."""
        from fastapi import HTTPException
        
        link_data = LinkCreate(
            original_url="not-a-valid-url",
            description="Test"
        )
        
        user = {
            "oid": "test-user",
            "name": "Test User",
            "tid": "test-tenant"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await LinkService.create_link(link_data, user)
        
        assert exc_info.value.status_code == 400
        assert "Invalid URL" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_link_success(self, monkeypatch):
        """Test successful link creation."""
        # Mock database operations
        mock_get_by_short_code = AsyncMock(return_value=None)
        mock_create_link = AsyncMock(return_value="test-id")
        
        monkeypatch.setattr(DatabaseManager, "get_link_by_short_code", mock_get_by_short_code)
        monkeypatch.setattr(DatabaseManager, "create_link", mock_create_link)
        
        link_data = LinkCreate(
            original_url="https://example.com",
            description="Test link"
        )
        
        user = {
            "oid": "test-user",
            "name": "Test User", 
            "tid": "test-tenant"
        }
        
        result = await LinkService.create_link(link_data, user)
        
        assert result.original_url == "https://example.com"
        assert result.description == "Test link"
        assert result.created_by == "test-user"
        assert result.created_by_name == "Test User"
        assert result.tenant_id == "test-tenant"
        assert result.click_count == 0
        
        # Verify database was called
        mock_create_link.assert_called_once()


@pytest.mark.unit
class TestDatabaseManager:
    """Unit tests for DatabaseManager."""

    def test_database_manager_exists(self):
        """Test that DatabaseManager class exists and has expected methods."""
        assert hasattr(DatabaseManager, 'get_link_by_short_code')
        assert hasattr(DatabaseManager, 'get_link_by_id')
        assert hasattr(DatabaseManager, 'create_link')
        assert hasattr(DatabaseManager, 'update_link')
        assert hasattr(DatabaseManager, 'delete_link')
        assert hasattr(DatabaseManager, 'increment_click_count')
        assert hasattr(DatabaseManager, 'get_link_analytics')


@pytest.mark.unit 
class TestModels:
    """Unit tests for Pydantic models."""

    def test_link_create_model(self):
        """Test LinkCreate model validation."""
        # Valid data
        link = LinkCreate(
            original_url="https://example.com",
            description="Test link"
        )
        assert link.original_url == "https://example.com"
        assert link.description == "Test link"
        assert link.custom_short_code is None

    def test_link_create_with_custom_code(self):
        """Test LinkCreate with custom short code."""
        link = LinkCreate(
            original_url="https://example.com",
            custom_short_code="custom123"
        )
        assert link.custom_short_code == "custom123"

    def test_link_update_model(self):
        """Test LinkUpdate model."""
        update = LinkUpdate(description="Updated description")
        assert update.description == "Updated description"
