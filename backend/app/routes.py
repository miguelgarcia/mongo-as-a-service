"""
Routes module for Mongo as a Service.
Defines API endpoints for CRUD operations on MongoDB instances.
All routes are protected with API key authentication.
"""

from fastapi import APIRouter, Depends, HTTPException
from . import auth, serialization

class Routes:
    def __init__(self, instances_service):
        self._instances_service = instances_service
        router = APIRouter(dependencies=[Depends(auth.get_api_key)])
        router.post("/instances", response_model=serialization.MongoInstanceOut, status_code=201)(self.create_instance)
        router.get("/instances", response_model=list[serialization.MongoInstanceOut])(self.list_instances)
        router.get("/instances/{instance_id}", response_model=serialization.MongoInstanceOut)(self.get_instance)
        router.put("/instances/{instance_id}")(self.update_instance)
        router.delete("/instances/{instance_id}", status_code=204)(self.delete_instance)
        self.router = router
        
    async def create_instance(self, data: serialization.MongoInstanceCreate):
        return await self._instances_service.create_instance(data.name)

    async def list_instances(self):
        return [r async for r in await self._instances_service.get_all_instances()]            

    async def get_instance(self, instance_id: str):
        instance = await self._instances_service.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        return instance

    async def update_instance(self, instance_id: str, data: serialization.MongoInstanceUpdate):
        return await self._instances_service.update_instance(instance_id, data.name)

    async def delete_instance(self, instance_id: str):
        await self._instances_service.delete_instance(instance_id)

