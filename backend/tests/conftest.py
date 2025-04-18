"""
Pytest configuration file for test fixtures.
"""
import pytest
import asyncio
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime
from fastapi.testclient import TestClient
from bson import ObjectId

from app.crud import InstancesCRUD
from app.routes import Routes
from app.main import app

@pytest.fixture
def mock_mongo_collection():
    """Returns a mongomock collection that mimics MongoDB."""
    return AsyncMongoMockClient()["db"]["collection"]


@pytest.fixture
def instances_crud(mock_mongo_collection):
    """Returns an InstancesCRUD instance with a mock collection."""
    return InstancesCRUD(mock_mongo_collection)


@pytest.fixture
def mock_instance_data():
    """Returns sample instance data."""
    return {
        "_id": ObjectId(),
        "name": "test-instance",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def mock_instances_collection_with_data(mock_mongo_collection, mock_instance_data):
    """Returns a mock collection with pre-inserted data."""
    async def setup():
        await mock_mongo_collection.insert_one(mock_instance_data)
        return mock_mongo_collection
    
    return asyncio.run(setup())


@pytest.fixture
def instance_id(mock_instance_data):
    """Returns the string representation of the mock instance ID."""
    return str(mock_instance_data["_id"])


@pytest.fixture
def api_key():
    """Return a known API key for testing."""
    return "test-api-key"

@pytest.fixture
def mock_env_api_key(monkeypatch, api_key):
    """Set the API_KEY environment variable for testing."""
    monkeypatch.setenv("API_KEY", api_key)
    yield
    # The environment variable will be reset after the test
