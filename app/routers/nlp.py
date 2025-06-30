"""
Natural Language Processing router for weather queries
Uses intelligent agent for smart decision making and multilingual responses
"""

from fastapi import APIRouter, HTTPException
import logging
import time

from ..services.agent_service import WeatherAgentService
from ..models.nlp import NLPQuery, NLPResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Natural Language"])

# Initialize the weather agent service
agent_service = WeatherAgentService()


@router.post("/", response_model=NLPResponse)
async def process_natural_language_query(nlp_query: NLPQuery):
    """
    Process a natural language query using intelligent agent behavior
    
    This endpoint implements intelligent reasoning that:
    - Only calls weather APIs for weather-related queries
    - Responds in the same language as the user's question
    - Uses smart decision making for better user experience
    
    Examples:
    - **Weather queries**: "What's the weather in Paris?", "¿Lloverá mañana?", "Quel temps fait-il?"
    - **Non-weather queries**: "Hello, how are you?", "What's your name?"
    
    - **query**: Natural language question in any supported language
    - **user_id**: Optional user identifier for personalization
    - **session_id**: Optional session identifier for context
    """
    try:
        # Use the intelligent agent service
        response = await agent_service.process_query(
            query=nlp_query.query,
            user_id=nlp_query.user_id,
            session_id=nlp_query.session_id
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query with intelligent agent: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing your query"
        )


@router.get("/health")
async def nlp_service_health():
    """Check NLP service health including the intelligent agent"""
    try:
        agent_healthy = await agent_service.health_check()
        weather_healthy = await agent_service.weather_service.health_check()
        
        return {
            "service": "nlp-agent",
            "status": "healthy" if (agent_healthy and weather_healthy) else "unhealthy",
            "components": {
                "agent": "healthy" if agent_healthy else "unhealthy",
                "weather": "healthy" if weather_healthy else "unhealthy"
            },
            "features": {
                "intelligent_reasoning": True,
                "language_detection": True,
                "smart_tool_calling": True
            },
            "openai_configured": bool(agent_service.api_key),
            "weather_configured": bool(agent_service.weather_service.api_key)
        }
    
    except Exception as e:
        logger.error(f"NLP agent service health check failed: {e}")
        return {
            "service": "nlp-agent",
            "status": "error",
            "error": str(e)
        }


@router.post("/test-agent")
async def test_agent_reasoning(nlp_query: NLPQuery):
    """
    Test the agent's reasoning capabilities with detailed information
    
    This endpoint shows the internal reasoning process for debugging and 
    understanding how the agent makes decisions.
    """
    try:
        # Process the query and return detailed reasoning information
        start_time = time.time()
        
        # Get the thought phase
        thought = await agent_service._think(nlp_query.query)
        
        # Execute actions
        actions = await agent_service._act(thought)
        
        # Get observation
        observation = await agent_service._observe(thought, actions)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "query": nlp_query.query,
            "agent_trace": {
                "thought": {
                    "is_weather_related": thought.is_weather_related,
                    "detected_language": thought.detected_language,
                    "confidence": thought.confidence,
                    "reasoning": thought.reasoning,
                    "suggested_actions": [action.value for action in thought.suggested_actions],
                    "parsed_query": thought.parsed_query.model_dump() if thought.parsed_query else None
                },
                "actions": [
                    {
                        "type": action.action_type.value,
                        "success": action.success,
                        "error": action.error,
                        "has_data": bool(action.data)
                    }
                    for action in actions
                ],
                "observation": {
                    "final_response": observation.final_response,
                    "language": observation.language,
                    "confidence": observation.confidence,
                    "needs_more_actions": observation.needs_more_actions
                }
            },
            "processing_time_ms": processing_time
        }
    
    except Exception as e:
        logger.error(f"Error in agent reasoning test: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error testing agent reasoning: {str(e)}"
        ) 