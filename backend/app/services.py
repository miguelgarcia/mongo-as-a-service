"""
Business logic for managing instances.
"""
from .model import MongoInstance

class InstancesService:
    def __init__(self, instances_repository, provisioner):
        self._instances_repository = instances_repository
        self._provisioner = provisioner

    async def create_instance(self, name: str):
        instance = await self._instances_repository.create_instance(name)
        await self._provisioner.provision_instance(instance.id)
        return MongoInstance(
            id=instance.id,
            name=instance.name,
            created_at=instance.created_at,
            status="provisioning",
            host=None,
            port=None,
        )

    async def get_instance(self, instance_id: str):
        instance = await self._instances_repository.get_instance(instance_id)
        return instance

    async def get_all_instances(self):
        return await self._instances_repository.get_all_instances()

    async def update_instance(self, instance_id: str, name: str):
        await self._instances_repository.update_instance(instance_id, name)

    async def delete_instance(self, instance_id: str):
        instance = await self._instances_repository.get_instance(instance_id)
        if instance is None:
            return None
        await self._provisioner.deprovision_instance(instance_id)
        return await self._instances_repository.delete_instance(instance_id)

