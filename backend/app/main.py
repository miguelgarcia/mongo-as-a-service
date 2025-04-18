"""
Main application module for Mongo as a Service.
Initializes the FastAPI application and includes routers.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import connect, MONGO_INSTANCES_COLLECTION
from .crud import InstancesCRUD
from .routes import Routes

def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mongo_client, mongo_db = await connect()
        try:
            instances_collection = mongo_db.get_collection(MONGO_INSTANCES_COLLECTION)
            instances_crud = InstancesCRUD(instances_collection)
            routes = Routes(instances_crud)
            app.include_router(routes.router)
            yield
        finally:
            mongo_client.close()
    app = FastAPI(title="Mongo as a Service", lifespan=lifespan)
    return app

app = create_app()

