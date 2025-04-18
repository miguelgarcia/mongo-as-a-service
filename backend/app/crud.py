"""
CRUD operations module for Mongo as a Service.
Provides functions for creating, reading, updating, and deleting MongoDB instances.
"""
from datetime import datetime
from bson.objectid import ObjectId

class InstancesCRUD:
    def __init__(self, instances_collection):
        self._instances_collection = instances_collection

    async def create_instance(self, name: str):
        instance = {
            "name": name,
            "created_at": datetime.utcnow()
        }
        result = await self._instances_collection.insert_one(instance)
        return {**instance, "id": str(result.inserted_id)}

    async def get_instance(self, instance_id: str):
        doc = await self._instances_collection.find_one({"_id": ObjectId(instance_id)})
        if doc:
            return {"id": str(doc["_id"]), "name": doc["name"], "created_at": doc["created_at"]}
        return None

    async def get_all_instances(self):
        cursor = self._instances_collection.find()
        return [
            {"id": str(doc["_id"]), "name": doc["name"], "created_at": doc["created_at"]}
            async for doc in cursor
        ]

    async def update_instance(self, instance_id: str, name: str):
        await self._instances_collection.update_one({"_id": ObjectId(instance_id)}, {"$set": {"name": name}})
        return await self.get_instance(instance_id)

    async def delete_instance(self, instance_id: str):
        await self._instances_collection.delete_one({"_id": ObjectId(instance_id)})

