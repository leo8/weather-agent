"""
Natural Language Processing models for the Weather Agent
Enhanced to support the Thought-Action-Observation (TAO) cycle
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NLPQuery(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language query in any supported language")
    user_id: Optional[str] = Field(None, description="Optional user identifier for context")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class ParsedQuery(BaseModel):
    """Structured data extracted from natural language query"""
    location: Optional[str] = Field(None, description="Extracted location")
    date_time: Optional[str] = Field(None, description="Extracted date/time reference")
    weather_aspect: Optional[str] = Field(None, description="Specific weather aspect requested")
    query_type: str = Field(..., description="Type of query (current, forecast, comparison, other, etc.)")
    confidence: float = Field(..., description="Confidence score of the parsing (0-1)")
    original_query: str = Field(..., description="Original user query")


class NLPResponse(BaseModel):
    """Response model for natural language processing with TAO cycle support"""
    parsed_query: ParsedQuery = Field(..., description="Structured query data")
    natural_response: str = Field(..., description="Human-readable response in user's language")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Associated weather data if applicable")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata including TAO trace")


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


# TAO Cycle specific models for detailed reasoning traces
class ReasoningTrace(BaseModel):
    """Detailed trace of the Thought-Action-Observation cycle"""
    thought: Dict[str, Any] = Field(..., description="Thought phase results")
    actions: list = Field(default_factory=list, description="Actions taken")
    observation: Dict[str, Any] = Field(..., description="Observation phase results")


class TAOResponse(BaseModel):
    """Extended response model showing detailed TAO cycle information"""
    query: str = Field(..., description="Original user query")
    reasoning_trace: ReasoningTrace = Field(..., description="Detailed TAO cycle trace")
    final_response: str = Field(..., description="Final response to user")
    processing_time_ms: float = Field(..., description="Total processing time")
    language_detected: str = Field(..., description="Detected user language")
    confidence: float = Field(..., description="Overall confidence score") 