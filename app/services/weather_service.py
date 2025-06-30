"""
Weather Service for fetching weather data from OpenWeatherMap API
"""

import httpx
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.weather import WeatherResponse, WeatherData, WeatherCondition, WeatherForecast

logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Base exception for weather service errors"""
    pass


class WeatherServiceUnavailable(WeatherServiceError):
    """Raised when the weather service is unavailable (API key issues, etc.)"""
    pass


class WeatherLocationNotFound(WeatherServiceError):
    """Raised when a location cannot be found"""
    pass


class WeatherService:
    """Service for interacting with weather APIs"""
    
    def __init__(self):
        """Initialize the weather service with OpenWeatherMap API."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if self.api_key:
            # Strip whitespace and newlines from the API key
            self.api_key = self.api_key.strip()
            if not self.api_key:
                logger.warning("OPENWEATHER_API_KEY is empty after stripping whitespace")
                self.api_key = None
        else:
            logger.warning("OPENWEATHER_API_KEY not found in environment variables")
        
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0"

    async def get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for a location"""
        if not self.api_key:
            raise WeatherServiceUnavailable("Weather service unavailable - API key not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.geocoding_url}/direct",
                    params={
                        "q": location,
                        "limit": 1,
                        "appid": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data:
                    return {
                        "lat": data[0]["lat"],
                        "lon": data[0]["lon"],
                        "name": data[0]["name"],
                        "country": data[0]["country"]
                    }
                raise WeatherLocationNotFound(f"Location '{location}' not found")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(f"API key authentication failed: {e}")
                raise WeatherServiceUnavailable("Weather service unavailable - API authentication failed")
            logger.error(f"HTTP error getting coordinates for {location}: {e}")
            raise WeatherServiceError(f"Error getting location data: {e}")
        except Exception as e:
            logger.error(f"Error getting coordinates for {location}: {e}")
            raise WeatherServiceError(f"Error getting coordinates: {e}")

    async def get_current_weather(self, location: str) -> Optional[WeatherResponse]:
        """Get current weather for a location"""
        try:
            # Get coordinates first
            coords = await self.get_coordinates(location)
            if not coords:
                raise WeatherLocationNotFound(f"Could not find coordinates for location: {location}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": coords["lat"],
                        "lon": coords["lon"],
                        "appid": self.api_key,
                        "units": "metric"  # Celsius
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Parse the response into our model
                weather_data = WeatherData(
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    pressure=data["main"]["pressure"],
                    visibility=data.get("visibility"),
                    uv_index=None  # Not available in current weather endpoint
                )

                conditions = [
                    WeatherCondition(
                        main=condition["main"],
                        description=condition["description"],
                        icon=condition["icon"]
                    )
                    for condition in data["weather"]
                ]

                return WeatherResponse(
                    location=coords["name"],
                    country=coords["country"],
                    coordinates={"lat": coords["lat"], "lon": coords["lon"]},
                    current_weather=weather_data,
                    conditions=conditions,
                    timestamp=datetime.fromtimestamp(data["dt"]),
                    source="OpenWeatherMap"
                )

        except WeatherServiceError:
            # Re-raise weather service specific errors
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise WeatherServiceUnavailable("Weather service unavailable - API authentication failed")
            logger.error(f"HTTP error fetching weather for {location}: {e}")
            raise WeatherServiceError(f"Error fetching weather data: {e}")
        except Exception as e:
            logger.error(f"Error fetching weather for {location}: {e}")
            raise WeatherServiceError(f"Error fetching weather: {e}")

    async def get_weather_forecast(self, location: str, days: int = 5) -> Optional[WeatherForecast]:
        """Get weather forecast for a location"""
        try:
            coords = await self.get_coordinates(location)
            if not coords:
                raise WeatherLocationNotFound(f"Could not find coordinates for location: {location}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": coords["lat"],
                        "lon": coords["lon"],
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                data = response.json()

                forecast_items = []
                for item in data["list"][:days * 8]:  # 8 forecasts per day (every 3 hours)
                    weather_data = WeatherData(
                        temperature=item["main"]["temp"],
                        feels_like=item["main"]["feels_like"],
                        humidity=item["main"]["humidity"],
                        pressure=item["main"]["pressure"],
                        visibility=item.get("visibility"),
                        uv_index=None
                    )

                    conditions = [
                        WeatherCondition(
                            main=condition["main"],
                            description=condition["description"],
                            icon=condition["icon"]
                        )
                        for condition in item["weather"]
                    ]

                    forecast_items.append({
                        "date": datetime.fromtimestamp(item["dt"]),
                        "weather_data": weather_data,
                        "conditions": conditions
                    })

                return WeatherForecast(
                    location=coords["name"],
                    forecast=forecast_items,
                    source="OpenWeatherMap"
                )

        except WeatherServiceError:
            # Re-raise weather service specific errors
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise WeatherServiceUnavailable("Weather service unavailable - API authentication failed")
            logger.error(f"HTTP error fetching forecast for {location}: {e}")
            raise WeatherServiceError(f"Error fetching forecast data: {e}")
        except Exception as e:
            logger.error(f"Error fetching forecast for {location}: {e}")
            raise WeatherServiceError(f"Error fetching forecast: {e}")

    async def health_check(self) -> bool:
        """Check if the weather service is accessible"""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": "London",
                        "appid": self.api_key
                    }
                )
                return response.status_code == 200
        except Exception:
            return False 