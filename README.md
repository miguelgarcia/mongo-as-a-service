mongo-as-a-service
---

This is a **toy project** to explore how to provide an easy way to allow users to create and manage
MongoDB instances in a Kubernetes cluster.

**Components**:

* Mongo kubernetes operator: Allows creating MongoDB instances from a single Kubernetes custom
resource.
* mongos-manager: Provides a HTTP API to manage mongo instances. Behind the scenes it interacts
with the Kubernetes cluster and MongoDB instances.
* Vault server: Stores secrets
* Kubernetes cluster: Hosts all components

For simplicity this project supports only MongoDB standalone instances (No replicas or HA are
supported).

**Features**

* Create / Delete MongoDB instance.
* List instances
* Get instance connection details
* Turn instance on/off
* View metrics: CPU, Disk, RAM
* Logs
* Trigger backup
* Restore backup
* Manage MongoDB users


# TODOs

* Provision k8s cluster and document steps: microk8s + metrics server + metrics-server
* Deploy vault and document steps