"""
Weather API router for direct weather data access
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from ..services.weather_service import WeatherService
from ..models.weather import WeatherResponse, WeatherForecast, WeatherQuery

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["Weather"])

# Initialize weather service
weather_service = WeatherService()


@router.get("/current/{location}", response_model=WeatherResponse)
async def get_current_weather(location: str):
    """
    Get current weather for a specific location
    
    - **location**: City name, coordinates, or location string
    """
    try:
        weather_data = await weather_service.get_current_weather(location)
        
        if not weather_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather data not found for location: {location}"
            )
        
        return weather_data
    
    except Exception as e:
        logger.error(f"Error fetching weather for {location}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while fetching weather data"
        )


@router.get("/forecast/{location}", response_model=WeatherForecast)
async def get_weather_forecast(
    location: str,
    days: int = Query(default=5, ge=1, le=10, description="Number of forecast days")
):
    """
    Get weather forecast for a specific location
    
    - **location**: City name, coordinates, or location string
    - **days**: Number of days to forecast (1-10)
    """
    try:
        forecast_data = await weather_service.get_weather_forecast(location, days)
        
        if not forecast_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Forecast data not found for location: {location}"
            )
        
        return forecast_data
    
    except Exception as e:
        logger.error(f"Error fetching forecast for {location}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while fetching forecast data"
        )


@router.post("/query", response_model=WeatherResponse)
async def query_weather(weather_query: WeatherQuery):
    """
    Query weather data using structured parameters
    
    - **location**: Required location
    - **date**: Optional date for historical/forecast data
    - **weather_type**: Optional specific weather aspect
    """
    try:
        # For now, just get current weather
        # In the future, this could handle date-specific queries
        weather_data = await weather_service.get_current_weather(weather_query.location)
        
        if not weather_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather data not found for location: {weather_query.location}"
            )
        
        return weather_data
    
    except Exception as e:
        logger.error(f"Error processing weather query: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while processing weather query"
        )


@router.get("/health")
async def weather_service_health():
    """Check weather service health"""
    try:
        is_healthy = await weather_service.health_check()
        
        return {
            "service": "weather",
            "status": "healthy" if is_healthy else "unhealthy",
            "api_configured": bool(weather_service.api_key),
            "timestamp": weather_service.__class__.__name__
        }
    
    except Exception as e:
        logger.error(f"Weather service health check failed: {e}")
        return {
            "service": "weather",
            "status": "error",
            "error": str(e)
        } 