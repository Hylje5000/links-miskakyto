import pytest
import asyncio
import os
import tempfile
from fastapi.testclient import TestClient
from httpx import AsyncClient
import aiosqlite

# Set test mode before importing the main app
os.environ["TEST_MODE"] = "true"

from main import app, init_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the test database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Initialize the test database
    old_db_path = "links.db"
    
    # Use the temporary database by setting an environment variable
    import os
    os.environ['TEST_DB_PATH'] = temp_db.name
    
    # Initialize the database
    await init_db()
    
    yield temp_db.name
    
    # Cleanup
    if 'TEST_DB_PATH' in os.environ:
        del os.environ['TEST_DB_PATH']
    os.unlink(temp_db.name)

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return {
        "oid": "test-user-id",
        "name": "Test User",
        "email": "test@example.com",
        "tid": "test-tenant-id"
    }

@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {"Authorization": "Bearer test-token"}
