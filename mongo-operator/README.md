mongo-operator
---

This operator abstracts and makes it easier to manage multiple MongoDB instances on a Kubernetes
cluster. The created instances are exposed using a service of NodePort type.

To create a MongoDB instance you need to first configure a secret with the credentials to be used
while initializing the DB, as follows:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: example-mongo-instance-credentials
  namespace: default
type: Opaque
data:
  username: c3VwZXJhZG1pbg== # superadmin
  password: c3VwZXJwYXNz     # superpass
```

Then you can create a new DB instance with this definition:

```yaml
apiVersion: mongo.miguelgarcia.dev/v1
kind: MongoInstance
metadata:
  name: example-mongo-instance
  namespace: default
spec:
  version: "8.0.6"
  storageSize: "10Gi"
  credentialsSecret: example-mongo-instance-credentials
```

After that, use `kubectl describe MongoInstance example-mongo-instance` to view the instance
health and port that are reported as part of the status, for example:

```
Status:
  Available Replicas:  1
  Port:                31959
```

You can connect using `mongosh 'mongodb://superadmin:superpass@${node_ip}:${port}/admin'`

# Running the controller locally / Development

To run the controller locally, go to the `controller` directory and run:

```bash
uv run poe run
```

This will target the Kubernetes cluster that you have currently configured for your user.

# Deployment

To enable the operator in a Kuberntes cluster execute the following steps:

1. Build and push the docker image from the `controller` directory
2. `kubectl apply -f crds/mongoinstances.yaml`
3. `kubectl create namespace mongoinstance-operator`
4. `kubectl apply -f run-on-k8s/manifest.yaml` (Update the image field as needed)