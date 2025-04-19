import kopf
from kr8s.objects import PersistentVolume, PersistentVolumeClaim, Service, StatefulSet

# TODO set owner of objects
# TODO update port when service is created
# TODO set credentials

def create_storage(name, namespace, spec):
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
    service.create()

def create_stateful_set(name, namespace, spec):
    stateful_set = StatefulSet({
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": name,
            "namespace": namespace
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
                        }]
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
    stateful_set.create()
 
def setup_mongo_instance(name, namespace, spec):
    create_storage(name, namespace, spec)
    create_external_service(name, namespace)
    create_stateful_set(name, namespace, spec)

def teardown_mongo_instance(name, namespace):
    # Delete StatefulSet
    stateful_set = StatefulSet({
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": name,
            "namespace": namespace
        }
    })
    stateful_set.delete()

    # Delete Service
    service = Service({
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "namespace": namespace
        }
    })
    service.delete()

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

    # Delete PersistentVolume
    pv = PersistentVolume({
        "apiVersion": "v1",
        "kind": "PersistentVolume",
        "metadata": {
            "name": f"{name}-pv"
        }
    })
    pv.delete()

@kopf.on.create('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def create_mongo(spec, name, namespace, logger, patch, **kwargs):
    logger.info(f"Creating MongoDB instance '{name}' in namespace '{namespace}'")

    setup_mongo_instance(name, namespace, spec)
    logger.info(f"MongoDB instance '{name}' created successfully")
    #patch.status['port'] = 27832

@kopf.on.update('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def update_mongo(spec, name, namespace, logger, **kwargs):
    logger.info(f"Updating MongoDB instance '{name}' in namespace '{namespace}'")

    # Example: Log spec or validate it
    version = spec.get('version', 'latest')
    logger.info(f"Requested version: {version}")

@kopf.on.delete('mongo.miguelgarcia.dev', 'v1', 'mongoinstances')
def delete_mongo(name, namespace, logger, **kwargs):
    logger.info(f"Deleting MongoDB instance '{name}' in namespace '{namespace}'")
    teardown_mongo_instance(name, namespace)
    # Example: Log spec or validate it
    logger.info(f"Instance '{name}' is being deleted")
