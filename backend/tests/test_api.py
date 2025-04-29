"""
Tests for API endpoints.
"""
import pytest

@pytest.mark.asyncio
async def test_create_instance(app_client, api_key):
    """Test creating an instance via the API."""
    async with app_client as ac:
        # Include API key in the headers - use the same key that was set in the environment
        headers = {"X-API-Key": api_key}
        response = await ac.post("/instances", headers=headers, json={"name": "test-instance"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-instance"
        assert "id" in data
        assert "created_at" in data

@pytest.mark.asyncio
async def test_list_instances_route(app_client, mock_instances_collection_with_data, api_key):
    """Test the list instances endpoint."""
    async with app_client as ac:
        headers = {"X-API-Key": api_key}
        response = await ac.get("/instances", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test-instance"

@pytest.mark.asyncio
async def test_get_instance_route(app_client, mock_instances_collection_with_data, instance_id, api_key):
    """Test the get instance endpoint."""
    async with app_client as ac:
        headers = {"X-API-Key": api_key}
        response = await ac.get(f"/instances/{instance_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
    
        assert data["id"] == instance_id
        assert data["name"] == "test-instance"

@pytest.mark.asyncio
async def test_get_instance_not_found_route(app_client, api_key):
    """Test the get instance endpoint."""
    async with app_client as ac:
        headers = {"X-API-Key": api_key}
        response = await ac.get(f"/instances/111", headers=headers)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_instance_route(app_client, mock_instances_collection_with_data, instance_id, api_key):
    """Test the update instance endpoint."""
    async with app_client as ac:
        headers = {"X-API-Key": api_key}
        response = await ac.put(f"/instances/{instance_id}", headers=headers, json={"name": "updated-instance"})
        assert response.status_code == 200
        response = await ac.get(f"/instances/{instance_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == instance_id
        assert data["name"] == "updated-instance"

@pytest.mark.asyncio
async def test_delete_instance_route(app_client, mock_instances_collection_with_data, instance_id, api_key):
    """Test the delete instance endpoint."""
    async with app_client as ac:
        headers = {"X-API-Key": api_key}
        response = await ac.delete(f"/instances/{instance_id}", headers=headers)
        assert response.status_code == 204
        response = await ac.get(f"/instances/{instance_id}", headers=headers)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_api_key(app_client, api_key):
    """Test creating an instance via the API."""
    async with app_client as ac:
        # Include API key in the headers - use the same key that was set in the environment
        headers = {"X-API-Key": "should-be-invalid"}
        response = await ac.post("/instances", headers=headers, json={"name": "test-instance"})
        assert response.status_code == 403