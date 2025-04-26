mongo-as-a-service
---

This is a **toy project** to explore how to provide an easy way to allow users to create and manage
MongoDB instances in a Kubernetes cluster.

Disclaimer: this is a toy project, don't try to use it on production environments. It doesn't 
support MongoDB instances with replicas and doesn't use Vault to manage secrets in a more secure
way

**Components**:

* Mongo kubernetes operator: Allows creating MongoDB instances from a single Kubernetes custom
resource.
* backend: Provides a HTTP API to manage mongo instances. Behind the scenes it interacts
with the Kubernetes cluster and MongoDB instances.
* Kubernetes cluster: Hosts all components

For simplicity this project supports only MongoDB standalone instances (No replicas or HA are
supported).

**Features**

* Create / Delete MongoDB instance.
* List instances
* Get instance connection details
* View metrics: CPU, Disk, RAM

