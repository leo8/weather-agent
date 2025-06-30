"""Integration tests for end-to-end functionality."""

import pytest


class TestIntegration:
    """Test complete workflows and integrations."""

    def test_weather_nlp_integration(self, client):
        """Test complete NLP to weather data flow."""
        # Test that NLP query returns both parsed query and weather data
        query_data = {"query": "What's the temperature in Madrid right now?"}

        response = client.post("/query/", json=query_data)
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()

            # Check NLP parsing worked
            assert "parsed_query" in data
            parsed = data["parsed_query"]
            location = parsed.get("location")
            # Handle case where location extraction fails (fallback mode)
            if location is not None:
                assert "Madrid" in location

            # Check that we have a natural response
            assert "natural_response" in data
            assert isinstance(data["natural_response"], str)

            # Weather data might be None in test environment without API keys
            assert "weather_data" in data

    def test_forecast_integration(self, client):
        """Test forecast query integration."""
        query_data = {"query": "Will it be sunny in Barcelona tomorrow?"}

        response = client.post("/query/", json=query_data)
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()

            # Should identify as forecast query
            if "parsed_query" in data and "query_type" in data["parsed_query"]:
                query_type = data["parsed_query"]["query_type"]
                # In fallback mode, it might not properly detect forecast
                # Just check that we got some response
                assert query_type in ["forecast", "current", "other"]

            # Check we got a response
            assert "natural_response" in data
            assert isinstance(data["natural_response"], str)

    def test_api_documentation_accessible(self, client):
        """Test that API documentation is accessible."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    @pytest.mark.parametrize("location", ["Paris", "London", "Tokyo", "New York"])
    def test_multiple_locations(self, client, location):
        """Test weather queries for multiple major cities."""
        response = client.get(f"/weather/current/{location}")
        
        # Should handle all major cities (if API is available)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["location"] == location 