import os
import pytest
import time
from collections.abc import Generator
from pytest_kind.cluster import KindCluster

@pytest.fixture(scope="session", autouse=True)
def k8s_cluster(request) -> Generator[KindCluster, None, None]:
    # Function copies from kr8s tests https://github.com/kr8s-org/kr8s/blob/main/conftest.py
    image = None
    if version := os.environ.get("KUBERNETES_VERSION"):
        image = f"kindest/node:v{version}"

    kind_cluster = KindCluster(
        name="pytest-kind",
        image=image,
    )
    kind_cluster.create()
    os.environ["KUBECONFIG"] = str(kind_cluster.kubeconfig_path)
    print("KUBECONFIG", os.environ["KUBECONFIG"])
    # CI fix, wait for default service account to be created before continuing
    while True:
        try:
            kind_cluster.kubectl("get", "serviceaccount", "default")
            break
        except Exception:
            time.sleep(1)
    # Configure CRDs
    kind_cluster.kubectl("apply", "-f", "../crds/mongoinstances.yaml")
    yield kind_cluster
    del os.environ["KUBECONFIG"]
    if not request.config.getoption("keep_cluster"):  # pragma: no cover
        kind_cluster.delete()