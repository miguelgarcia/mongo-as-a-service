"""
Pytest configuration file for test fixtures.
"""
import pytest
import asyncio
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from bson import ObjectId

from app.repository import MongoInstancesRepository
from app.services import InstancesService
from app.provisioner import InstanceDetails

@pytest.fixture
def mock_mongo_collection():
    """Returns a mongomock collection that mimics MongoDB."""
    return AsyncMongoMockClient()["db"]["collection"]


@pytest.fixture
def mongo_instances_repository(mock_mongo_collection):
    """Returns an MongoInstancesRepository instance with a mock collection."""
    return MongoInstancesRepository(mock_mongo_collection)

@pytest.fixture
def mock_provisioner():
    """Returns a mock provisioner."""
    class MockProvisioner:
        def __init__(self):
            self.provisioned_instances = []

        async def provision_instance(self, instance_id):
            self.provisioned_instances.append(instance_id)

        async def deprovision_instance(self, instance_id):
            if instance_id in self.provisioned_instances:
                self.provisioned_instances.remove(instance_id)
    
    return MockProvisioner()

@pytest.fixture
def mongo_instances_service(mongo_instances_repository, mock_provisioner):
    """Returns an InstancesService."""
    return InstancesService(mongo_instances_repository, mock_provisioner)


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

@pytest.fixture
def app_client(mongo_instances_service, mock_env_api_key):
    """Returns a test client for the FastAPI app configured with a mock Mongo DB."""
    from app.main import create_app
    app = create_app(mongo_instances_service)
    class WithClient:
        def __init__(self, app):
            self.app = app

        async def __aenter__(self):
            self.lifespan_manager = LifespanManager(self.app)
            self.client = AsyncClient(
                transport=ASGITransport(app=self.app), base_url="http://test"
            )
            await self.lifespan_manager.__aenter__()
            return await self.client.__aenter__()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            await self.lifespan_manager.__aexit__(exc_type, exc_val, exc_tb)
    return WithClient(app)
