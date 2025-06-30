"""Test health endpoints."""

import pytest


def test_app_health(client):
    """Test main application health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "weather-agent"
    assert data["version"] == "0.1.0"


def test_weather_service_health(client):
    """Test weather service health check."""
    response = client.get("/weather/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "weather"
    assert data["status"] in ["healthy", "unhealthy"]


def test_nlp_service_health(client):
    """Test NLP service health check."""
    response = client.get("/query/health")  # Fixed endpoint path
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "nlp-agent"
    assert data["status"] in ["healthy", "unhealthy"]


def test_calendar_service_health(client):
    """Test calendar service health check."""
    response = client.get("/calendar/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "calendar"
    assert data["status"] in ["healthy", "unhealthy"]


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Weather Agent API" in data["message"]
    assert "version" in data 