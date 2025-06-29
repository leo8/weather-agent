"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_weather_query():
    """Sample weather query for testing."""
    return {"query": "What's the weather in Paris today?"}


@pytest.fixture
def sample_forecast_query():
    """Sample forecast query for testing."""
    return {"query": "Will it rain tomorrow in Tokyo?"} 