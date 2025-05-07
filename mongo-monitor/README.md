mongo-monitor
---

This program monitors `MongoInstance` resources on Kubernetes and updates their status in the
backend calling its API.

You need to configure the following environment variables:

* `BACKEND_API_URL` backend API base URL
* `BACKEND_API_KEY` backend API key
* `PUBLIC_HOST` used to set the host of the monitored mongo instances.

## Running

```bash
uv run poe run
```
