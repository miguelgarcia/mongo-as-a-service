"""
Tests for API routes endpoints.
"""
import pytest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_instance_route(instances_crud):
    """Test the create instance endpoint."""
    from app.routes import Routes
    from app.serialization import MongoInstanceCreate
    
    routes = Routes(instances_crud)
    data = MongoInstanceCreate(name="new-instance")
    result = await routes.create_instance(data)
    
    assert result["name"] == "new-instance"
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_list_instances_route(instances_crud, mock_instances_collection_with_data):
    """Test the list instances endpoint."""
    from app.routes import Routes
    
    routes = Routes(instances_crud)
    results = await routes.list_instances()
    
    assert len(results) == 1
    assert results[0]["name"] == "test-instance"


@pytest.mark.asyncio
async def test_get_instance_route(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test the get instance endpoint."""
    from app.routes import Routes
    
    routes = Routes(instances_crud)
    result = await routes.get_instance(instance_id)
    
    assert result["id"] == instance_id
    assert result["name"] == "test-instance"


@pytest.mark.asyncio
async def test_get_instance_not_found_route(instances_crud):
    """Test the get instance endpoint with a non-existent ID."""
    from app.routes import Routes
    from bson import ObjectId
    
    routes = Routes(instances_crud)
    non_existent_id = str(ObjectId())
    
    with pytest.raises(HTTPException) as exc_info:
        await routes.get_instance(non_existent_id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Instance not found"


@pytest.mark.asyncio
async def test_update_instance_route(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test the update instance endpoint."""
    from app.routes import Routes
    from app.serialization import MongoInstanceCreate
    
    routes = Routes(instances_crud)
    data = MongoInstanceCreate(name="updated-instance")
    result = await routes.update_instance(instance_id, data)
    
    assert result["id"] == instance_id
    assert result["name"] == "updated-instance"


@pytest.mark.asyncio
async def test_delete_instance_route(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test the delete instance endpoint."""
    from app.routes import Routes
    
    routes = Routes(instances_crud)
    await routes.delete_instance(instance_id)
