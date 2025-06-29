"""
Natural Language Processing models for the Weather Agent
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NLPQuery(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language weather query")
    user_id: Optional[str] = Field(None, description="Optional user identifier for context")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class ParsedQuery(BaseModel):
    """Structured data extracted from natural language query"""
    location: Optional[str] = Field(None, description="Extracted location")
    date_time: Optional[str] = Field(None, description="Extracted date/time reference")
    weather_aspect: Optional[str] = Field(None, description="Specific weather aspect requested")
    query_type: str = Field(..., description="Type of query (current, forecast, comparison, etc.)")
    confidence: float = Field(..., description="Confidence score of the parsing (0-1)")
    original_query: str = Field(..., description="Original user query")


class NLPResponse(BaseModel):
    """Response model for natural language processing"""
    parsed_query: ParsedQuery = Field(..., description="Structured query data")
    natural_response: str = Field(..., description="Human-readable response")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Associated weather data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class CalendarEventQuery(BaseModel):
    """Request model for calendar-weather integration"""
    query: str = Field(..., description="Natural language query about calendar and weather")
    date_range: Optional[str] = Field(None, description="Date range for calendar events")
    calendar_id: Optional[str] = Field(None, description="Specific calendar to query")


class CalendarWeatherResponse(BaseModel):
    """Response for calendar-weather integration"""
    events: list = Field(default_factory=list, description="Calendar events")
    weather_recommendations: str = Field(..., description="Weather-based recommendations")
    natural_response: str = Field(..., description="Human-readable response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp") 