"""
Business logic for managing instances.
"""
from datetime import datetime, timezone
from .model import MongoInstance
from .serialization import MongoInstanceCreateOut

class InstancesService:
    def __init__(self, instances_repository, provisioner):
        self._instances_repository = instances_repository
        self._provisioner = provisioner

    async def create_instance(self, name: str):
        """
        Creates and provisions a new MongoDB instance.
        """
        instance = MongoInstance(
            id=None,
            name=name,
            created_at=datetime.now(tz=timezone.utc),
            status="provisioning",
            host=None,
            port=None,
        )
        await self._instances_repository.create_instance(instance)
        # Generate a random root password
        root_password = MongoInstance.generate_password()
        await self._provisioner.provision_instance(instance, root_password)
        return MongoInstanceCreateOut(
            id=instance.id,
            name=instance.name,
            created_at=instance.created_at,
            status=instance.status,
            host=instance.host,
            port=instance.port,
            password=root_password,
        )

    async def get_instance(self, instance_id: str):
        instance = await self._instances_repository.get_instance(instance_id)
        # TODO(mike) instead of refreshing the instance here, we should let the operator update
        # the status of the instance when there are changes
        if instance:
            await self._provisioner.refresh_instance(instance)
        return instance

    async def get_all_instances(self):
        return await self._instances_repository.get_all_instances()

    async def update_instance(self, instance_id: str, name: str):
        await self._instances_repository.update_instance(instance_id, name)

    async def delete_instance(self, instance_id: str):
        instance = await self._instances_repository.get_instance(instance_id)
        if instance is None:
            raise ValueError(f"Instance with ID {instance_id} not found")
        await self._provisioner.deprovision_instance(instance)
        await self._instances_repository.delete_instance(instance_id)

