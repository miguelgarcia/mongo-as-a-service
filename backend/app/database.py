"""
Database module for Mongo as a Service.
Provides methods to connect to MongoDB and retrieve collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_INSTANCES_COLLECTION = "mongo_instances"
DB_NAME = os.getenv("MONGODB_NAME")


async def connect():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client[DB_NAME]
    return client, db
