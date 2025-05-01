"""
Main application module for Mongo as a Service.
Initializes the FastAPI application and includes routers.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import connect, MONGO_INSTANCES_COLLECTION
from .repository import MongoInstancesRepository
from .services import InstancesService
from .provisioner import Provisioner
from .routes import Routes

def create_app(instances_service=None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal instances_service
        mongo_client = None
        try:
            if instances_service is None:
                mongo_client, mongo_db = await connect()
                instances_collection = mongo_db.get_collection(MONGO_INSTANCES_COLLECTION)
                instances_repository = MongoInstancesRepository(instances_collection)
                provisioner = Provisioner()
                instances_service = InstancesService(instances_repository, provisioner)
            routes = Routes(instances_service)
            app.include_router(routes.router)
            yield
        finally:
            if mongo_client:
                await mongo_client.close()
    app = FastAPI(title="Mongo as a Service", lifespan=lifespan)
    return app


