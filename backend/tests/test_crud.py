"""
Tests for CRUD operations on MongoDB instances.
"""
import pytest
from bson import ObjectId


@pytest.mark.asyncio
async def test_create_instance(instances_crud):
    """Test creating a new MongoDB instance."""
    name = "test-instance"
    result = await instances_crud.create_instance(name)
    
    assert result["name"] == name
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_instance(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test retrieving a MongoDB instance by ID."""
    result = await instances_crud.get_instance(instance_id)
    
    assert result["id"] == instance_id
    assert result["name"] == "test-instance"
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_instance_not_found(instances_crud):
    """Test retrieving a non-existent MongoDB instance."""
    non_existent_id = str(ObjectId())
    result = await instances_crud.get_instance(non_existent_id)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_instances(instances_crud, mock_instances_collection_with_data):
    """Test retrieving all MongoDB instances."""
    results = await instances_crud.get_all_instances()
    
    assert len(results) == 1
    assert results[0]["name"] == "test-instance"
    assert "id" in results[0]
    assert "created_at" in results[0]


@pytest.mark.asyncio
async def test_update_instance(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test updating a MongoDB instance."""
    new_name = "updated-instance"
    result = await instances_crud.update_instance(instance_id, new_name)
    
    assert result["id"] == instance_id
    assert result["name"] == new_name


@pytest.mark.asyncio
async def test_delete_instance(instances_crud, mock_instances_collection_with_data, instance_id):
    """Test deleting a MongoDB instance."""
    await instances_crud.delete_instance(instance_id)
    
    result = await instances_crud.get_instance(instance_id)
    assert result is None
