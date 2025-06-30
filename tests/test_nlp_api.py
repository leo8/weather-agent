"""Test NLP API endpoints with the new agent service."""

import pytest


class TestNLPAPI:
    """Test natural language processing endpoints."""

    def test_main_query_endpoint(self, client, sample_weather_query):
        """Test main query endpoint with agent service."""
        response = client.post("/query/", json=sample_weather_query)
        
        # Should return 200 if APIs are configured, 503 if not
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "parsed_query" in data
            assert "natural_response" in data
            assert "weather_data" in data
            assert "processing_time_ms" in data

    def test_forecast_query_endpoint(self, client, sample_forecast_query):
        """Test forecast query via main endpoint."""
        response = client.post("/query/", json=sample_forecast_query)
        
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "parsed_query" in data
            # Should detect forecast query type
            if "query_type" in data["parsed_query"]:
                assert "forecast" in data["parsed_query"]["query_type"]

    def test_health_endpoint(self, client):
        """Test NLP service health endpoint."""
        response = client.get("/query/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert "components" in data
        assert "features" in data
        
        # Check agent-specific features
        features = data["features"]
        assert "intelligent_reasoning" in features
        assert "language_detection" in features
        assert "smart_tool_calling" in features

    def test_agent_test_endpoint(self, client):
        """Test agent testing endpoint."""
        test_query = {"query": "What's the weather in Paris?"}
        
        response = client.post("/query/test-agent", json=test_query)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "agent_trace" in data
            assert "processing_time_ms" in data
            
            # Check agent trace structure
            trace = data["agent_trace"]
            assert "thought" in trace
            assert "actions" in trace
            assert "observation" in trace

    def test_query_endpoint_invalid_input(self, client):
        """Test query endpoint with invalid input."""
        response = client.post("/query/", json={})
        assert response.status_code == 422  # Validation error

    def test_query_endpoint_empty_query(self, client):
        """Test query endpoint with empty query."""
        response = client.post("/query/", json={"query": ""})
        # Agent handles empty queries gracefully with fallback parsing
        assert response.status_code in [200, 400, 503]

    def test_complex_weather_query(self, client):
        """Test complex weather query with agent intelligence."""
        complex_query = {
            "query": "Should I bring an umbrella to my meeting in San Francisco this afternoon?"
        }
        
        response = client.post("/query/", json=complex_query)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "natural_response" in data
            # Agent should provide helpful advice
            response_text = data["natural_response"].lower()
            assert any(word in response_text for word in ["umbrella", "rain", "weather", "francisco"])

    def test_non_weather_query(self, client):
        """Test non-weather query to verify agent intelligence."""
        non_weather_query = {
            "query": "Hello, how are you today?"
        }
        
        response = client.post("/query/", json=non_weather_query)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "natural_response" in data
            # Should not have weather data for non-weather queries
            # (unless API fallback still provides it)
            # Focus on ensuring response is reasonable
            assert len(data["natural_response"]) > 0

    def test_multilingual_query(self, client):
        """Test multilingual query handling."""
        spanish_query = {
            "query": "¿Lloverá mañana en Madrid?"
        }
        
        response = client.post("/query/", json=spanish_query)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "natural_response" in data
            # Agent should detect language and respond appropriately
            assert len(data["natural_response"]) > 0 