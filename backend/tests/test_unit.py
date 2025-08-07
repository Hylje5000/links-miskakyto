import pytest
from unittest.mock import Mock, AsyncMock
import os

# Set test mode before importing
os.environ["TEST_MODE"] = "true"
os.environ["AZURE_TENANT_ID"] = "test-tenant"
os.environ["AZURE_CLIENT_ID"] = "test-client"

from app.services.service import LinkService
from app.models.schemas import LinkCreate, LinkUpdate
from app.core.database import DatabaseManager


@pytest.mark.unit
class TestLinkService:
    """Unit tests for LinkService."""

    def test_generate_short_code(self):
        """Test short code generation."""
        code = LinkService.generate_short_code()
        assert isinstance(code, str)
        assert 6 <= len(code) <= 14  # Word-based codes are variable length
        assert code.isalnum()  # Should contain only letters and numbers
        
        # Generate multiple codes to ensure they're different
        codes = [LinkService.generate_short_code() for _ in range(10)]
        assert len(set(codes)) == 10  # All should be unique

    @pytest.mark.asyncio
    async def test_create_link_invalid_url(self):
        """Test creating a link with invalid URL."""
        from fastapi import HTTPException
        
        # Bypass pydantic validation to test service-level check
        link_data = LinkCreate.model_construct(
            original_url="not-a-valid-url",
            description="Test",
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
    async def test_create_link_invalid_custom_code(self):
        """Custom short code outside allowed pattern should fail."""
        from fastapi import HTTPException

        link_data = LinkCreate.model_construct(
            original_url="https://example.com",
            custom_short_code="invalid code!",
        )

        user = {
            "oid": "test-user",
            "name": "Test User",
            "tid": "test-tenant",
        }

        with pytest.raises(HTTPException) as exc_info:
            await LinkService.create_link(link_data, user)

        assert exc_info.value.status_code == 400
        assert "Custom short code" in exc_info.value.detail

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

    def test_link_create_invalid_custom_code(self):
        """Invalid custom short codes should raise ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            LinkCreate(
                original_url="https://example.com",
                custom_short_code="ab",
            )

        with pytest.raises(ValidationError):
            LinkCreate(
                original_url="https://example.com",
                custom_short_code="invalid code!",
            )

    def test_link_create_invalid_url(self):
        """Invalid URLs should raise ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            LinkCreate(original_url="not-a-valid-url")

    def test_link_update_model(self):
        """Test LinkUpdate model."""
        update = LinkUpdate(description="Updated description")
        assert update.description == "Updated description"


@pytest.mark.unit
class TestWordGenerator:
    """Unit tests for WordCodeGenerator."""

    def test_generate_word_code(self):
        """Test word-based code generation."""
        from app.services.generator import WordCodeGenerator
        
        code = WordCodeGenerator.generate_word_code()
        assert isinstance(code, str)
        assert 6 <= len(code) <= 14
        assert code.isalnum()
        assert code.islower()  # Should be lowercase
        
        # Generate multiple codes
        codes = [WordCodeGenerator.generate_word_code() for _ in range(20)]
        assert len(set(codes)) >= 15  # Most should be unique (allowing some duplicates)

    def test_generate_numbered_code(self):
        """Test numbered word-based code generation."""
        from app.services.generator import WordCodeGenerator
        
        code = WordCodeGenerator.generate_numbered_code()
        assert isinstance(code, str)
        assert code.isalnum()
        assert any(char.isdigit() for char in code)  # Should contain numbers
        assert any(char.isalpha() for char in code)  # Should contain letters

    def test_appropriateness_check(self):
        """Test the appropriateness filter."""
        from app.services.generator import WordCodeGenerator
        
        # Test appropriate codes
        assert WordCodeGenerator.is_appropriate("happycat") == True
        assert WordCodeGenerator.is_appropriate("bluebird") == True
        assert WordCodeGenerator.is_appropriate("fastrun") == True
        
        # Test inappropriate codes (basic filter)
        assert WordCodeGenerator.is_appropriate("hellcat") == False
        assert WordCodeGenerator.is_appropriate("damnthing") == False


@pytest.mark.unit
class TestBackupCleanup:
    """Test backup cleanup functionality."""
    
    def test_backup_cleanup_logic(self):
        """Test that backup cleanup logic works correctly."""
        import tempfile
        import glob
        import os
        import time
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a fake database file
            db_file = os.path.join(temp_dir, "test.db")
            with open(db_file, "w") as f:
                f.write("fake database content")
            
            # Create 7 fake backup files (more than the limit of 5)
            backup_files = []
            for i in range(7):
                backup_file = f"{db_file}.backup_{int(time.time()) - (60 * i)}"  # Different timestamps
                with open(backup_file, "w") as f:
                    f.write(f"backup content {i}")
                backup_files.append(backup_file)
                time.sleep(0.01)  # Small delay to ensure different timestamps
            
            # Verify we have 7 backup files
            pattern = f"{db_file}.backup_*"
            all_backups = glob.glob(pattern)
            assert len(all_backups) == 7
            
            # Simulate the cleanup logic from alembic_integration.py
            BACKUP_LIMIT = 5
            backup_files = glob.glob(pattern)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remove old backups beyond the limit
            removed_count = 0
            if len(backup_files) > BACKUP_LIMIT:
                for old_backup in backup_files[BACKUP_LIMIT:]:
                    try:
                        os.remove(old_backup)
                        removed_count += 1
                    except Exception:
                        pass
            
            # Verify cleanup worked
            remaining_backups = glob.glob(pattern)
            assert len(remaining_backups) == BACKUP_LIMIT
            assert removed_count == 2  # Should have removed 2 files (7 - 5 = 2)
