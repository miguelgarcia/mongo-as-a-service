"""
Authentication module for Mongo as a Service.
Implements API key-based authentication for securing endpoints.
"""

from fastapi import Header, HTTPException
import os


def get_api_key(x_api_key: str = Header(...)):
    API_KEY = os.getenv("API_KEY")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
