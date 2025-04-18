"""
Tests for authentication functionality.
"""
import pytest
from fastapi import HTTPException
from app.auth import get_api_key


def test_valid_api_key(mock_env_api_key, api_key):
    """Test that valid API key passes authentication."""
    # Should not raise an exception
    get_api_key(api_key)


def test_invalid_api_key(mock_env_api_key, api_key):
    """Test that invalid API key raises an exception."""
    with pytest.raises(HTTPException) as exc_info:
        get_api_key("invalid-key")
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Invalid API Key"
