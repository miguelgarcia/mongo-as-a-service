"""
CRUD operations module for Mongo as a Service.
Provides functions for creating, reading, updating, and deleting MongoDB instances in the DB.
"""
from datetime import datetime
from bson.objectid import ObjectId
from .model import MongoInstance

class MongoInstancesRepository:
    def __init__(self, instances_collection):
        self._instances_collection = instances_collection

    async def create_instance(self, instance: MongoInstance):
        result = await self._instances_collection.insert_one(instance.model_dump())
        instance.id = str(result.inserted_id)
        return instance

    async def get_instance(self, instance_id: str):
        try:
            doc = await self._instances_collection.find_one({"_id": ObjectId(instance_id)})
            if doc:
                return MongoInstance.model_validate({"id": str(doc["_id"]), "name": doc["name"], "created_at": doc["created_at"]})
        except Exception as e:
            print(f"Error retrieving instance: {e}")
        return None

    async def get_all_instances(self):
        cursor = self._instances_collection.find()
        return (
            MongoInstance.model_validate({"id": str(doc["_id"]), "name": doc["name"], "created_at": doc["created_at"]})
            async for doc in cursor
        )

    async def update_instance(self, instance_id: str, name: str):
        await self._instances_collection.update_one({"_id": ObjectId(instance_id)}, {"$set": {"name": name}})

    async def delete_instance(self, instance_id: str):
        await self._instances_collection.delete_one({"_id": ObjectId(instance_id)})

