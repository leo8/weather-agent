"""
Natural Language Processing router for weather queries
"""

from fastapi import APIRouter, HTTPException
import logging
import time

from ..services.nlp_service import NLPService
from ..services.weather_service import WeatherService, WeatherServiceUnavailable, WeatherLocationNotFound, WeatherServiceError
from ..models.nlp import NLPQuery, NLPResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Natural Language"])

# Initialize services
nlp_service = NLPService()
weather_service = WeatherService()


@router.post("/", response_model=NLPResponse)
async def process_natural_language_query(nlp_query: NLPQuery):
    """
    Process a natural language weather query
    
    This is the main endpoint that combines NLP processing with weather data retrieval
    to provide natural language responses to weather questions.
    
    - **query**: Natural language weather question (e.g., "What's the weather in Paris?")
    - **user_id**: Optional user identifier for personalization
    - **session_id**: Optional session identifier for context
    """
    start_time = time.time()
    
    try:
        # Step 1: Parse the natural language query
        parsed_query = await nlp_service.parse_weather_query(nlp_query.query)
        
        if not parsed_query:
            raise HTTPException(
                status_code=400,
                detail="Could not parse the weather query"
            )
        
        # Step 2: Get weather data if location is available
        weather_data = None
        if parsed_query.location:
            try:
                if parsed_query.query_type == "forecast":
                    forecast = await weather_service.get_weather_forecast(parsed_query.location)
                    if forecast:
                        weather_data = forecast.model_dump()
                else:
                    current = await weather_service.get_current_weather(parsed_query.location)
                    if current:
                        weather_data = current.model_dump()
            except WeatherServiceUnavailable:
                # API key not configured - continue without weather data
                weather_data = None
            except (WeatherLocationNotFound, WeatherServiceError):
                # Location not found or other weather service error - continue without weather data
                weather_data = None
        
        # Step 3: Generate natural language response
        if weather_data:
            natural_response = await nlp_service.generate_natural_response(
                parsed_query, weather_data
            )
        else:
            if parsed_query.location:
                natural_response = f"I couldn't find weather information for {parsed_query.location}. Please check the location name and try again."
            else:
                natural_response = "I couldn't determine the location from your query. Could you please specify a city or location?"
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return NLPResponse(
            parsed_query=parsed_query,
            natural_response=natural_response,
            weather_data=weather_data,
            processing_time_ms=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing NLP query: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing your query"
        )


@router.get("/health")
async def nlp_service_health():
    """Check NLP service health"""
    try:
        nlp_healthy = await nlp_service.health_check()
        weather_healthy = await weather_service.health_check()
        
        return {
            "service": "nlp",
            "status": "healthy" if (nlp_healthy and weather_healthy) else "unhealthy",
            "components": {
                "nlp": "healthy" if nlp_healthy else "unhealthy",
                "weather": "healthy" if weather_healthy else "unhealthy"
            },
            "openai_configured": bool(nlp_service.api_key),
            "weather_configured": bool(weather_service.api_key)
        }
    
    except Exception as e:
        logger.error(f"NLP service health check failed: {e}")
        return {
            "service": "nlp",
            "status": "error",
            "error": str(e)
        }


@router.post("/parse")
async def parse_query_only(nlp_query: NLPQuery):
    """
    Parse a natural language query without fetching weather data
    
    Useful for testing the NLP parsing capabilities or when you only
    need to understand the structure of a query.
    """
    try:
        parsed_query = await nlp_service.parse_weather_query(nlp_query.query)
        
        if not parsed_query:
            raise HTTPException(
                status_code=400,
                detail="Could not parse the weather query"
            )
        
        return {
            "parsed_query": parsed_query.model_dump(),
            "query": nlp_query.query
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while parsing query"
        ) 