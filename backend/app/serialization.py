"""
Models module for Mongo as a Service.
Defines Pydantic models for request validation and response serialization.
"""
from pydantic import BaseModel
from datetime import datetime

class MongoInstanceCreate(BaseModel):
    name: str

class MongoInstanceOut(MongoInstanceCreate):
    id: str
    created_at: datetime
