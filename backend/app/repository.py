"""
CRUD operations module for Mongo as a Service.
Provides functions for creating, reading, updating, and deleting MongoDB instances in the DB.
"""

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import AsyncGenerator
from .model import MongoInstance


class MongoInstancesRepository:
    def __init__(self, instances_collection: AsyncIOMotorCollection):
        self._instances_collection = instances_collection

    async def create_instance(self, instance: MongoInstance) -> MongoInstance:
        result = await self._instances_collection.insert_one(
            instance.model_dump(exclude={"id"})
        )
        instance.id = str(result.inserted_id)
        return instance

    async def get_instance(self, instance_id: str) -> MongoInstance | None:
        try:
            doc = await self._instances_collection.find_one(
                {"_id": ObjectId(instance_id)}
            )
            if doc:
                return MongoInstance.model_validate(
                    {"id": str(doc["_id"]), **doc}, strict=False
                )
        except Exception as e:
            print(f"Error retrieving instance: {e}")
        return None

    async def get_all_instances(self) -> AsyncGenerator[MongoInstance, None]:
        cursor = self._instances_collection.find()
        return (
            MongoInstance.model_validate({"id": str(doc["_id"]), **doc}, strict=False)
            async for doc in cursor
        )

    async def update_instance(self, instance_id: str, update) -> None:
        updates = update.model_dump()
        # Remove fields with None values from the update dictionary
        updates = {key: value for key, value in updates.items() if value is not None}
        await self._instances_collection.update_one(
            {"_id": ObjectId(instance_id)}, {"$set": updates}
        )

    async def delete_instance(self, instance_id: str) -> None:
        await self._instances_collection.delete_one({"_id": ObjectId(instance_id)})
