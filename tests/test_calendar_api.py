"""Test calendar API endpoints."""

import pytest


class TestCalendarAPI:
    """Test calendar integration endpoints."""

    def test_calendar_weather_check(self, client):
        """Test calendar weather check endpoint."""
        query_data = {
            "query": "Should I reschedule my outdoor events this week?"
        }
        
        response = client.post("/calendar/weather-check", json=query_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "events" in data
            assert "weather_recommendations" in data
            assert "natural_response" in data

    def test_calendar_events_endpoint(self, client):
        """Test calendar events endpoint."""
        response = client.get("/calendar/events")
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_calendar_outdoor_events(self, client):
        """Test outdoor events filtering."""
        response = client.get("/calendar/outdoor-events")
        assert response.status_code == 200
        
        data = response.json()
        assert "outdoor_events" in data
        assert isinstance(data["outdoor_events"], list)

    def test_calendar_weather_check_invalid_input(self, client):
        """Test calendar weather check with invalid input."""
        response = client.post("/calendar/weather-check", json={})
        assert response.status_code == 422  # Validation error 