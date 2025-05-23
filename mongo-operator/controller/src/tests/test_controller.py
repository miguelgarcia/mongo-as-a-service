import time
from kr8s.objects import Pod, new_class
from kopf.testing import KopfRunner

MongoInstanceResource = new_class(
    kind="MongoInstance",
    version="mongo.miguelgarcia.dev/v1",
    namespaced=True,
    plural="mongoinstances",
)

def test_create_instance(k8s_cluster):
    """
    Test the creation of a MongoDB instance in the cluster.
    This test will create a MongoDB instance and check if the corresponding Pod is started.
    """
    with KopfRunner(['run', '-A', '--verbose', 'src/controller.py']) as runner:
        try:
            time.sleep(10)  # give it some time to react and to sleep and to retry
            k8s_cluster.kubectl("apply", "-f", "src/tests/instance.yaml")
            time.sleep(10)  # give it some time to react and to sleep and to retry
            # Check resources created
            pod = Pod.get(name="test-mongo-instance-0", namespace="default")
            assert pod is not None
            assert pod.status.phase == "Running"
            instance = MongoInstanceResource.get(name="test-mongo-instance", namespace="default")
            assert instance is not None
            assert instance.status.get("availableReplicas") == 1
        finally:
            k8s_cluster.kubectl("delete", "-f", "src/tests/instance.yaml")
    assert runner.exit_code == 0
    assert runner.exception is None