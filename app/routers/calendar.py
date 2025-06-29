"""
Calendar integration router for weather-based recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..services.calendar_service import CalendarService
from ..services.weather_service import WeatherService
from ..models.nlp import CalendarEventQuery, CalendarWeatherResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calendar", tags=["Calendar"])

# Initialize services
calendar_service = CalendarService()
weather_service = WeatherService()


@router.post("/weather-check", response_model=CalendarWeatherResponse)
async def check_calendar_weather(calendar_query: CalendarEventQuery):
    """
    Check weather conditions for calendar events and provide recommendations
    
    This endpoint combines calendar events with weather data to provide
    weather-based recommendations for your scheduled activities.
    
    - **query**: Natural language query about calendar and weather
    - **date_range**: Optional date range (defaults to next 7 days)
    - **calendar_id**: Optional specific calendar to check
    """
    try:
        # Parse date range or default to next 7 days
        start_date = datetime.now()
        if calendar_query.date_range:
            # Simple parsing - in production, you'd want more robust date parsing
            if "tomorrow" in calendar_query.date_range.lower():
                start_date = datetime.now() + timedelta(days=1)
                end_date = start_date + timedelta(days=1)
            elif "week" in calendar_query.date_range.lower():
                end_date = start_date + timedelta(days=7)
            else:
                end_date = start_date + timedelta(days=7)
        else:
            end_date = start_date + timedelta(days=7)
        
        # Get calendar events
        events = await calendar_service.get_events(start_date, end_date)
        
        # Get weather data for the first location or default location
        # In a real implementation, you might extract location from events
        # For now, we'll use a default location or extract from query
        location = "New York"  # Default location
        weather_data = await weather_service.get_current_weather(location)
        
        if not weather_data:
            raise HTTPException(
                status_code=404,
                detail=f"Could not get weather data for {location}"
            )
        
        # Generate recommendations
        recommendations = await calendar_service.generate_weather_recommendations(
            events, weather_data.dict()
        )
        
        # Generate natural language response
        natural_response = f"""
        I found {len(events)} events in your calendar for the next week.
        Here are my weather-based recommendations:
        
        {recommendations}
        
        Current weather in {location}: {weather_data.current_weather.temperature}°C, {weather_data.conditions[0].description}
        """
        
        return CalendarWeatherResponse(
            events=events,
            weather_recommendations=recommendations,
            natural_response=natural_response.strip()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking calendar weather: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while checking calendar weather"
        )


@router.get("/events")
async def get_calendar_events(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to look ahead")
):
    """
    Get calendar events for the next N days
    
    - **days**: Number of days to retrieve events for (1-30)
    """
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        events = await calendar_service.get_events(start_date, end_date)
        
        return {
            "events": events,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "count": len(events)
        }
    
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching calendar events"
        )


@router.get("/outdoor-events")
async def get_outdoor_events(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to look ahead")
):
    """
    Get weather-dependent events from calendar
    
    - **days**: Number of days to retrieve events for (1-30)
    """
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        events = await calendar_service.get_events(start_date, end_date)
        outdoor_events = await calendar_service.check_outdoor_events(events)
        
        return {
            "outdoor_events": outdoor_events,
            "total_events": len(events),
            "outdoor_count": len(outdoor_events),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting outdoor events: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching outdoor events"
        )


@router.get("/health")
async def calendar_service_health():
    """Check calendar service health"""
    try:
        calendar_healthy = await calendar_service.health_check()
        weather_healthy = await weather_service.health_check()
        
        return {
            "service": "calendar",
            "status": "healthy" if (calendar_healthy and weather_healthy) else "unhealthy",
            "components": {
                "calendar": "healthy" if calendar_healthy else "unhealthy",
                "weather": "healthy" if weather_healthy else "unhealthy"
            },
            "calendar_configured": bool(calendar_service.credentials_path or calendar_service.api_key),
            "weather_configured": bool(weather_service.api_key)
        }
    
    except Exception as e:
        logger.error(f"Calendar service health check failed: {e}")
        return {
            "service": "calendar",
            "status": "error",
            "error": str(e)
        } 