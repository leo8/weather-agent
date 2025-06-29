"""Test weather API endpoints."""

import pytest


class TestWeatherAPI:
    """Test weather-related API endpoints."""

    def test_current_weather_valid_location(self, client):
        """Test current weather endpoint with valid location."""
        response = client.get("/weather/current/Paris")
        
        # Should return 200 if API key is configured, 503 if not
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["location"] == "Paris"
            assert "current_weather" in data
            assert "temperature" in data["current_weather"]

    def test_current_weather_invalid_location(self, client):
        """Test current weather endpoint with invalid location."""
        response = client.get("/weather/current/InvalidCityName123")
        
        # Should return 404 for location not found, or 503 if API is unavailable
        assert response.status_code in [404, 503]

    def test_forecast_endpoint(self, client):
        """Test forecast endpoint."""
        response = client.get("/weather/forecast/London")
        
        # Should return 200 if API key is configured, 503 if not
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["location"] == "London"
            assert "forecast" in data
            assert len(data["forecast"]) > 0

    def test_forecast_with_days_parameter(self, client):
        """Test forecast endpoint with days parameter."""
        response = client.get("/weather/forecast/Tokyo?days=3")
        
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["location"] == "Tokyo"

    def test_weather_query_endpoint(self, client):
        """Test structured weather query endpoint."""
        query_data = {
            "location": "Berlin",
            "query_type": "current"
        }
        
        response = client.post("/weather/query", json=query_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["location"] == "Berlin" 