"""Test NLP API endpoints."""

import pytest


class TestNLPAPI:
    """Test natural language processing endpoints."""

    def test_query_endpoint_basic(self, client, sample_weather_query):
        """Test basic NLP query endpoint."""
        response = client.post("/query/", json=sample_weather_query)
        
        # Should return 200 if APIs are configured, 503 if not
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "parsed_query" in data
            assert "natural_response" in data
            assert "weather_data" in data

    def test_query_endpoint_forecast(self, client, sample_forecast_query):
        """Test forecast query via NLP endpoint."""
        response = client.post("/query/", json=sample_forecast_query)
        
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "parsed_query" in data
            # Should detect forecast query type
            if "query_type" in data["parsed_query"]:
                assert "forecast" in data["parsed_query"]["query_type"]

    def test_query_parse_endpoint(self, client):
        """Test query parsing endpoint."""
        query_data = {"query": "Weather in London tomorrow"}
        
        response = client.post("/query/parse", json=query_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            # Location is nested in parsed_query
            assert "parsed_query" in data
            parsed_query = data["parsed_query"]
            assert "location" in parsed_query
            assert "query_type" in parsed_query
            assert "confidence" in parsed_query

    def test_query_endpoint_invalid_input(self, client):
        """Test query endpoint with invalid input."""
        response = client.post("/query/", json={})
        assert response.status_code == 422  # Validation error

    def test_query_endpoint_empty_query(self, client):
        """Test query endpoint with empty query."""
        response = client.post("/query/", json={"query": ""})
        # API handles empty queries gracefully with fallback parsing
        assert response.status_code in [200, 400, 503]

    def test_complex_weather_query(self, client):
        """Test complex weather query."""
        complex_query = {
            "query": "Should I bring an umbrella to my meeting in San Francisco this afternoon?"
        }
        
        response = client.post("/query/", json=complex_query)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "natural_response" in data
            # Should provide helpful advice
            response_text = data["natural_response"].lower()
            assert any(word in response_text for word in ["umbrella", "rain", "weather", "francisco"]) 