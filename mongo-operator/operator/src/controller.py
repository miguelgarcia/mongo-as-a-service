"""
Kopf operator for the MongoInstance resource.
This module registers handlers to listen for events on "mongoinstances" k8s resources and takes
care of creating and managing the MongoDB instance, including its storage, service, and stateful set
in the cluster.
"""
import kopf
import logging
from kr8s.objects import PersistentVolume, PersistentVolumeClaim, Service, StatefulSet, new_class

MongoInstanceResource = new_class(
  kind="MongoInstance",
  version="mongo.miguelgarcia.dev/v1",
  namespaced=True,
  plural="mongoinstances"
)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Or INFO, WARNING, etc.
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
async def create_storage(name, namespace, spec):
    """
    Create a PersistentVolume and PersistentVolumeClaim for the MongoDB instance.
    """
    requested_storage = spec.get('storage', '1Gi')
    pv = PersistentVolume({
        "apiVersion": "v1",
        "kind": "PersistentVolume",
        "metadata": {
            "name": f"{name}-pv"
        },
        "spec": {
            "capacity": {
                "storage": requested_storage
            },
            "accessModes": ["ReadWriteOnce"],
            "hostPath": {
                "path": f"/data/{name}"
            }
        }
    })
    await pv.async_create()

    # Create PersistentVolumeClaim
    pvc = PersistentVolumeClaim({
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": f"{name}-pvc",
            "namespace": namespace
        },
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": requested_storage
                }
            }
        }
    })
    await pvc.async_create()


async def create_external_service(name, namespace):
    """
    Create a NodePort service for the MongoDB instance.
    This service will expose the MongoDB instance to the outside world.
    """
    service = Service({
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "namespace": namespace
        },
        "spec": {
            "type": "NodePort",
            "selector": {
                "app": name
            },
            "ports": [{
                "protocol": "TCP",
                "port": 27017,
                "targetPort": 27017
            }]
        }
    })
    kopf.adopt(service.to_dict())
    await service.async_create()
    return service


async def create_stateful_set(name, namespace, spec):
    """
    Create a StatefulSet for the MongoDB instance.
    This StatefulSet will manage the MongoDB pods and ensure that they are
    running and healthy.
    """
    credentials_secret = spec.get('credentialsSecret')
    stateful_set = StatefulSet({
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "serviceName": name,
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": name
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": name
                    }
                },
                "spec": {
                    "containers": [{
                        "name": name,
                        "image": f"mongo:{spec.get('version', 'latest')}",
                        "ports": [{
                            "containerPort": 27017
                        }],
                        "volumeMounts": [{
                            "mountPath": "/data/db",
                            "name": f"storage"
                        }],
                        "env": [
                            {
                                "name": "MONGO_INITDB_ROOT_USERNAME",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": credentials_secret,
                                        "key": "username"
                                    }
                                }
                            },
                            {
                                "name": "MONGO_INITDB_ROOT_PASSWORD",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": credentials_secret,
                                        "key": "password"
                                    }
                                }
                            }
                        ]
                    }],
                    "volumes": [{
                        "name": f"storage",
                        "persistentVolumeClaim": {
                            "claimName": f"{name}-pvc"
                        }
                    }]
                }
            }
        }
    })
    kopf.adopt(stateful_set.to_dict())
    await stateful_set.async_create()


async def setup_mongo_instance(name, namespace, spec):
    """
    Setup the MongoDB instance by creating the necessary resources.
    """
    await create_storage(name, namespace, spec)
    await create_stateful_set(name, namespace, spec)
    return await create_external_service(name, namespace)


async def teardown_mongo_instance(name, namespace):
    """
    Teardown the MongoDB instance by deleting the resources.
    """
    # Delete StatefulSet
    try:
        stateful_set = StatefulSet({
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": name,
                "namespace": namespace
            }
        })
        await stateful_set.async_delete()
    except Exception as e:
        logger.warning(f"Error deleting StatefulSet: {e}")

    # Delete Service
    try:
        service = Service({
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": namespace
            }
        })
        await service.async_delete()
    except Exception as e:
        logger.warning(f"Error deleting Service: {e}")

    try:
        # Delete PersistentVolumeClaim
        pvc = PersistentVolumeClaim({
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{name}-pvc",
                "namespace": namespace
            }
        })
        await pvc.async_delete()
    except Exception as e:
        logger.warning(f"Error deleting PersistentVolumeClaim: {e}")

    try:
        # Delete PersistentVolume
        pv = PersistentVolume({
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {
                "name": f"{name}-pv"
            }
        })
        await pv.async_delete()
    except Exception as e:
        logger.warning(f"Error deleting PersistentVolume: {e}")

@kopf.on.create('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
async def create_mongo(spec, name, namespace, logger, patch, resource, **kwargs):
    logger.info(
        f"Creating MongoDB instance '{name}' in namespace '{namespace}'")
    service = await setup_mongo_instance(name, namespace, spec)
    await service.async_refresh()
    port = service.spec.ports[0].nodePort
    logger.info(
        f"MongoDB instance '{name}' on port {port} created successfully")
    patch.status['port'] = port


@kopf.on.update('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
async def update_mongo(spec, name, namespace, logger, **kwargs):
    logger.warning(f"Not implemented")


@kopf.on.delete('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
async def delete_mongo(name, namespace, logger, **kwargs):
    logger.info(
        f"Deleting MongoDB instance '{name}' in namespace '{namespace}'")
    await teardown_mongo_instance(name, namespace)
    # Example: Log spec or validate it
    logger.info(f"Instance '{name}' is being deleted")


@kopf.on.update('apps', 'v1', 'statefulsets', field='status')
async def update_statefulset(meta, new, name, namespace, logger, **kwargs):
    # Check if the StatefulSet is owned by a MongoInstance resource
    owner_references = meta.get("ownerReferences", [])
    mongo_instance_ref = next(
        (owner for owner in owner_references if owner.get("kind") == "MongoInstance"),
        None
    )
    if not mongo_instance_ref:
        return
    available_replicas = new.get("availableReplicas", 0)
    logger.info(
        f"Updating MongoInstance '{mongo_instance_ref.get('name')}' with available replicas: {available_replicas}")
    kopf.event(
        {
            "apiVersion": "mongo.miguelgarcia.dev/v1",
            "kind": "MongoInstance",
            "metadata": {
                "name": mongo_instance_ref.get("name"),
                "namespace": namespace,
                "uid": mongo_instance_ref.get("uid"),
            },
        },
        type="Normal",
        reason="StatefulSetUpdated",
        message=f"Available replicas updated to {available_replicas}",
    )
    mongo_instance = await MongoInstanceResource.async_get(
        name=mongo_instance_ref.get("name"),
        namespace=namespace,
    )

    # Patch the custom resource
    await mongo_instance.async_patch({
        "status": {
            "availableReplicas": available_replicas
        }
    })

if __name__ == "__main__":
    # Run the Kopf operator loop
    kopf.run(clusterwide=True, standalone=True)