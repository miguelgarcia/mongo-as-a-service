"""This program monitors mongo instances running on a Kubernetes cluster and tracks updates to the
status of the instances in calling backend APIs."""

import asyncio
import os
import httpx
from kr8s.asyncio import watch
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Or INFO, WARNING, etc.
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

backend_api_url =  os.getenv("BACKEND_API_URL")
if not backend_api_url:
    raise ValueError("BACKEND_API_URL environment variable is not set.")
backend_api_key = os.getenv("BACKEND_API_KEY")
if not backend_api_key:
    raise ValueError("BACKEND_API_KEY environment variable is not set.")

# Hostname of the public-facing service used to populate the host field in the backend API
public_host = os.getenv("PUBLIC_HOST")
if not public_host:
    raise ValueError("PUBLIC_HOST environment variable is not set.")

async def update_instace(instance_id, port=None, status=None):
    """Update the instance in the backend API."""
    url = f"{backend_api_url}/instances/{instance_id}"
    headers = {
        "x-api-key": backend_api_key,
        "Content-Type": "application/json"
    }
    data = {}
    if port:
        data["port"] = port
    if status:
        data["status"] = status
    data["host"] = public_host
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=data)
        if response.status_code == 200:
            logging.info(f"Successfully updated instance {instance_id} in backend API.")
        else:
            logging.error(f"Failed to update instance {instance_id} in backend API: {response.text}")

async def handle_event(event_type, instance):
    instance_id = instance.annotations.get("mongo-instance-id")
    if not instance_id:
        logging.warning("No mongo-instance-id found in annotations.")
        return
    if event_type == "ADDED":
        return
    elif event_type == "MODIFIED":
        status = instance.status
        if status:
            logging.info(f"Instance {instance_id} modified with status: {status}")
            port = status.get("port")
            available_replicas = status.get("availableReplicas")
            instance_status = "ready" if available_replicas else "not ready"
            await update_instace(instance_id, port=port, status=instance_status)
            print(f"Instance {instance_id} modified with port: {port}, available replicas: {available_replicas}")
        else:
            logging.warning(f"Instance {instance_id} modified but no status found.")
    
async def watch_instances():
    async for event in watch("mongoinstances", namespace="default"):
        event_type, instance = event
        logging.info(f"Event: {event_type}, Instance: {instance['metadata']['name']}")
        try:
            await handle_event(event_type, instance)
        except Exception as e:
            logging.error(f"Error handling event: {e}")

if __name__ == "__main__":
    asyncio.run(watch_instances())