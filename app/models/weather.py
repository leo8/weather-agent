"""
Weather data models using Pydantic for validation and serialization
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WeatherQuery(BaseModel):
    """Request model for weather queries"""
    location: str = Field(..., description="Location for weather query (city, coordinates, etc.)")
    date: Optional[str] = Field(None, description="Date for weather query (YYYY-MM-DD format)")
    weather_type: Optional[str] = Field(None, description="Specific weather aspect (temperature, precipitation, etc.)")


class WeatherCondition(BaseModel):
    """Weather condition details"""
    main: str = Field(..., description="Main weather condition (Clear, Rain, etc.)")
    description: str = Field(..., description="Detailed weather description")
    icon: str = Field(..., description="Weather icon code")


class WeatherData(BaseModel):
    """Core weather data"""
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    uv_index: Optional[float] = Field(None, description="UV index")


class WeatherResponse(BaseModel):
    """Response model for weather data"""
    location: str = Field(..., description="Location name")
    country: str = Field(..., description="Country code")
    coordinates: dict = Field(..., description="Latitude and longitude")
    current_weather: WeatherData = Field(..., description="Current weather conditions")
    conditions: List[WeatherCondition] = Field(..., description="Weather conditions")
    timestamp: datetime = Field(..., description="Data timestamp")
    source: str = Field(default="OpenWeatherMap", description="Data source")


class ForecastItem(BaseModel):
    """Individual forecast item"""
    date: datetime = Field(..., description="Forecast date and time")
    weather_data: WeatherData = Field(..., description="Weather data for this time")
    conditions: List[WeatherCondition] = Field(..., description="Weather conditions")


class WeatherForecast(BaseModel):
    """Extended weather forecast"""
    location: str = Field(..., description="Location name")
    forecast: List[ForecastItem] = Field(..., description="Forecast items")
    source: str = Field(default="OpenWeatherMap", description="Data source") 