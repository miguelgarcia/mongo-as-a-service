"""
Kopf handlers for MongoDB operator.
This module registers handlers to listen for events on "mongoinstances" k8s resources and takes
care of creating and managing the MongoDB instance, including its storage, service, and stateful set
in the cluster.
"""
import kopf
import logging
from pprint import pprint
from kr8s.objects import PersistentVolume, PersistentVolumeClaim, Service, StatefulSet, new_class

MongoInstanceResource = new_class(
  kind="MongoInstance",
  version="mongo.miguelgarcia.dev/v1",
  namespaced=True,
  plural="mongoinstances"
)

logger = logging.getLogger(__name__)

# TODO set owner of objects
# TODO update port when service is created
# TODO set credentials


def create_storage(name, namespace, spec):
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
    pv.create()

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
    pvc.create()


def create_external_service(name, namespace):
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
    service.create()
    return service


def create_stateful_set(name, namespace, spec):
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
                            "name": f"{name}-storage"
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
                        "name": f"{name}-storage",
                        "persistentVolumeClaim": {
                            "claimName": f"{name}-pvc"
                        }
                    }]
                }
            }
        }
    })
    kopf.adopt(stateful_set.to_dict())
    stateful_set.create()


def setup_mongo_instance(name, namespace, spec):
    """
    Setup the MongoDB instance by creating the necessary resources.
    """
    create_storage(name, namespace, spec)
    create_stateful_set(name, namespace, spec)
    return create_external_service(name, namespace)


def teardown_mongo_instance(name, namespace):
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
        stateful_set.delete()
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
        service.delete()
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
        pvc.delete()
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
        pv.delete()
    except Exception as e:
        logger.warning(f"Error deleting PersistentVolume: {e}")

# Event handlers


@kopf.on.create('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def create_mongo(spec, name, namespace, logger, patch, resource, **kwargs):
    logger.info(
        f"Creating MongoDB instance '{name}' in namespace '{namespace}'")
    service = setup_mongo_instance(name, namespace, spec)
    service.refresh()
    port = service.spec.ports[0].nodePort
    logger.info(
        f"MongoDB instance '{name}' on port {port} created successfully")
    patch.status['port'] = port


@kopf.on.update('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def update_mongo(spec, name, namespace, logger, **kwargs):
    logger.warning(f"Not implemented")


@kopf.on.delete('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def delete_mongo(name, namespace, logger, **kwargs):
    logger.info(
        f"Deleting MongoDB instance '{name}' in namespace '{namespace}'")
    teardown_mongo_instance(name, namespace)
    # Example: Log spec or validate it
    logger.info(f"Instance '{name}' is being deleted")


@kopf.on.update('apps', 'v1', 'statefulsets', field='status')
def update_statefulset(meta, new, name, namespace, logger, **kwargs):
    print(f"StatefulSet '{name}' in namespace '{namespace}' updated")
    # Check if the StatefulSet is owned by a MongoInstance resource
    owner_references = meta.get("ownerReferences", [])
    print(f"Owner references: {owner_references}")
    mongo_instance_owner = next(
        (owner for owner in owner_references if owner.get("kind") == "MongoInstance"),
        None
    )
    print(f"MongoInstance owner: {mongo_instance_owner}")
    if not mongo_instance_owner:
        return
    available_replicas = new.get("availableReplicas", 0)
    logger.info(
        f"Updating MongoInstance '{mongo_instance_owner.get('name')}' with available replicas: {available_replicas}")
    kopf.event(
        {
            "apiVersion": "mongo.miguelgarcia.dev/v1",
            "kind": "MongoInstance",
            "metadata": {
                "name": mongo_instance_owner.get("name"),
                "namespace": namespace,
            },
        },
        type="Normal",
        reason="StatefulSetUpdated",
        message=f"Available replicas updated to {available_replicas}",
    )
    cr = MongoInstanceResource.get(
        name=mongo_instance_owner.get("name"),
        namespace=namespace,
    )

    # Patch the custom resource
    cr.patch({
        "status": {
            "availableReplicas": available_replicas
        }
    })