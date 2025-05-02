"""
Models module for Mongo as a Service.
Defines Pydantic models for request validation and response serialization.
"""
from pydantic import BaseModel
from datetime import datetime

class MongoInstanceCreate(BaseModel):
    name: str

class MongoInstanceUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    host: str | None = None
    port: int | None = None

class MongoInstanceOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    status: str | None
    host: str | None
    port: int | None

class MongoInstanceCreateOut(MongoInstanceOut):
    password: str | None = None