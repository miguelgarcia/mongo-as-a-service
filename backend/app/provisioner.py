"""Provisioner for MongoDB instances. It takes care of creating and deleting the MongoDB instance
in Kubernetes using the MongoInstance resource kind."""

from base64 import b64encode
from kr8s.objects import new_class, Secret

MongoInstanceResource = new_class(
    kind="MongoInstance",
    version="mongo.miguelgarcia.dev/v1",
    namespaced=True,
    plural="mongoinstances",
)


class Provisioner:
    async def provision_instance(self, instance, root_password):
        """Provisions a MongoDB instance in Kubernetes using the MongoInstance kind."""
        k8s_name = f"mongo-instance-{instance.id}"
        k8s_credentials = f"mongo-credentials-{instance.id}"
        k8s_namespace = "default"
        secret = Secret(
            {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": k8s_credentials,
                    "namespace": k8s_namespace,
                },
                "type": "Opaque",
                "data": {
                    "username": b64encode("root".encode()).decode(),
                    "password": b64encode(root_password.encode()).decode(),
                },
            }
        )
        await secret.async_create()
        k8s_resource = MongoInstanceResource(
            {
                "metadata": {
                    "name": k8s_name,
                    "namespace": "default",
                    "annotations": {"mongo-instance-id": instance.id},
                },
                "spec": {
                    "storageSize": "5Gi",
                    "version": "latest",
                    "credentialsSecret": k8s_credentials,
                },
            }
        )
        await k8s_resource.async_create()

    async def deprovision_instance(self, instance):
        """Deprovisions a MongoDB instance in Kubernetes deleting the associated MongoInstance
        resource."""
        k8s_name = f"mongo-instance-{instance.id}"
        k8s_namespace = "default"
        k8s_credentials = f"mongo-credentials-{instance.id}"
        k8s_resource = MongoInstanceResource(
            {"metadata": {"name": k8s_name, "namespace": k8s_namespace}}
        )
        secret = Secret(
            {"metadata": {"name": k8s_credentials, "namespace": k8s_namespace}}
        )
        if await secret.async_exists():
            await secret.async_delete()
        if await k8s_resource.async_exists():
            await k8s_resource.async_delete()
