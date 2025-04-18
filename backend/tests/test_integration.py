"""
Integration tests for the API endpoints.
"""
import pytest
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from app.main import create_app  # Import your FastAPI app

@pytest.mark.asyncio
async def test_create_instance(mock_env_api_key, api_key):
    """Test creating an instance via the API."""
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Include API key in the headers - use the same key that was set in the environment
            headers = {"X-API-Key": api_key}
            response = await ac.post("/instances", headers=headers, json={"name": "test-instance"})
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "test-instance"
            assert "id" in data
            assert "created_at" in data

@pytest.mark.asyncio
async def test_get_instance(mock_env_api_key, api_key):
    """Test retrieving an instance via the API."""
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Create an instance first
            headers = {"X-API-Key": api_key}
            create_response = await ac.post("/instances", headers=headers, json={"name": "test-instance"})
            assert create_response.status_code == 201
            instance_id = create_response.json()["id"]

            # Retrieve the created instance
            response = await ac.get(f"/instances/{instance_id}", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == instance_id
            assert data["name"] == "test-instance"

@pytest.mark.asyncio
async def test_list_instances(mock_env_api_key, api_key):
    """Test listing all instances via the API."""
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            headers = {"X-API-Key": api_key}

            # Create multiple instances
            await ac.post("/instances", headers=headers, json={"name": "instance-1"})
            await ac.post("/instances", headers=headers, json={"name": "instance-2"})

            # List all instances
            response = await ac.get("/instances", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 2  # Ensure at least two instances exist
            assert any(instance["name"] == "instance-1" for instance in data)
            assert any(instance["name"] == "instance-2" for instance in data)

@pytest.mark.asyncio
async def test_delete_instance(mock_env_api_key, api_key):
    """Test deleting an instance via the API."""
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Create an instance first
            headers = {"X-API-Key": api_key}
            create_response = await ac.post("/instances", headers=headers, json={"name": "test-instance"})
            assert create_response.status_code == 201
            instance_id = create_response.json()["id"]

            # Delete the created instance
            delete_response = await ac.delete(f"/instances/{instance_id}", headers=headers)
            assert delete_response.status_code == 204

            # Verify the instance no longer exists
            get_response = await ac.get(f"/instances/{instance_id}", headers=headers)
            assert get_response.status_code == 404
