"""
Test configuration for the refactored API.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import tempfile

# Set test mode before importing the app
os.environ["TEST_MODE"] = "true"
# Use a temp file for test database instead of in-memory to persist across connections
test_db_path = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

from main import create_app
from app.core.database import init_db

# Create app instance for testing
app = create_app(enable_lifespan=False)


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(test_db):
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture(scope="session")
async def test_db():
    """Create a test database."""
    # Initialize the database tables
    await init_db()
    yield test_db_path
    # Cleanup
    try:
        os.unlink(test_db_path)
    except FileNotFoundError:
        pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
