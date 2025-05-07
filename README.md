mongo-as-a-service
---

This is a **toy project** to explore how to provide an easy way to allow users to create and manage
MongoDB instances in a Kubernetes cluster.

Disclaimer: this is a toy project, don't try to use it on production environments. It doesn't 
support MongoDB instances with replicas and doesn't use Vault to manage secrets in a more secure
way

**Components**:

* `mongo-operator/`: Kubernetes operator that allows creating MongoDB instances from a single
Kubernetes custom resource.
* `backend/`: Provides a HTTP API to manage mongo instances. Behind the scenes it interacts
with the Kubernetes cluster and MongoDB instances.
* `mongo-monitor/`: Monitors mongo instances in Kubernetes and tracks their status calling the
backend API.

For simplicity this project supports only MongoDB standalone instances (No replicas or HA are
supported).

**Demo**

The demo shows how to invoke the backend API to create an instance, connect to it using mongosh and then delete it.

![](demo.gif)

**Features**

* Create / Delete MongoDB instance.
* List instances
* Get instance connection details (host and port)
