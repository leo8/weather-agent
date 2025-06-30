"""
Tests for the intelligent weather agent implementation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.agent_service import WeatherAgentService, ActionType, AgentThought, AgentAction, AgentObservation
from app.models.nlp import ParsedQuery, NLPResponse


class TestWeatherAgent:
    """Test the intelligent weather agent implementation"""

    @pytest.fixture
    def agent_service(self):
        """Create an agent service for testing"""
        return WeatherAgentService()

    @pytest.mark.asyncio
    async def test_weather_query_english(self, agent_service):
        """Test agent with a weather query in English"""
        
        # Test with a mocked OpenAI client
        with patch.object(agent_service, 'client') as mock_client:
            # Mock the thought phase
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = """
            {
                "is_weather_related": true,
                "detected_language": "en",
                "confidence": 0.9,
                "reasoning": "User is asking for current weather in Paris",
                "suggested_actions": ["weather_current"],
                "parsed_query": {
                    "location": "Paris",
                    "date_time": null,
                    "weather_aspect": null,
                    "query_type": "current"
                }
            }
            """
            mock_client.chat.completions.create.return_value = mock_response
            
            # Mock weather service
            mock_weather_data = {
                "location": "Paris",
                "current_weather": {"temperature": 22.5, "humidity": 65},
                "conditions": [{"description": "sunny", "icon": "01d"}]
            }
            
            with patch.object(agent_service.weather_service, 'get_current_weather') as mock_weather:
                mock_weather.return_value = MagicMock()
                mock_weather.return_value.model_dump.return_value = mock_weather_data
                
                # Test the full agent cycle
                result = await agent_service.process_query("What's the weather in Paris?")
                
                # Verify the response
                assert isinstance(result, NLPResponse)
                assert result.parsed_query.location == "Paris"
                assert result.parsed_query.query_type == "current"
                assert "Paris" in result.natural_response
                assert result.weather_data is not None

    def test_action_types(self):
        """Test that all action types are properly defined"""
        
        assert ActionType.GET_CURRENT_WEATHER.value == "get_current_weather"
        assert ActionType.GET_WEATHER_FORECAST.value == "get_weather_forecast"
        assert ActionType.DIRECT_RESPONSE.value == "direct_response"
        assert ActionType.NO_ACTION.value == "no_action"


async def demonstrate_agent_capabilities():
    """Demonstration of the intelligent weather agent capabilities"""
    
    print("🤖 Weather Agent Capability Demonstration")
    print("=" * 50)
    
    agent = WeatherAgentService()
    
    test_queries = [
        "What's the weather in Paris?",
        "¿Lloverá mañana en Madrid?", 
        "Hello, how are you?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        try:
            with patch.object(agent.weather_service, 'get_current_weather'), \
                 patch.object(agent.weather_service, 'get_weather_forecast'):
                
                result = await agent.process_query(query)
                
                print(f"   Query Type: {result.parsed_query.query_type}")
                print(f"   Response: {result.natural_response}")
                print(f"   Weather Data Available: {result.weather_data is not None}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ Agent demonstration complete!")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_agent_capabilities())
