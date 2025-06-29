"""
Natural Language Processing Service using OpenAI for parsing weather queries
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from ..models.nlp import ParsedQuery, NLPResponse

logger = logging.getLogger(__name__)


class NLPService:
    """Service for natural language processing of weather queries"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        elif AsyncOpenAI:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI package not installed. Natural language processing disabled.")

    async def parse_weather_query(self, query: str) -> Optional[ParsedQuery]:
        """Parse a natural language weather query into structured data"""
        if not self.client:
            logger.error("OpenAI client not available")
            return self._fallback_parse(query)

        try:
            system_prompt = """
            You are a weather query parser. Extract structured information from natural language weather queries.
            
            Return a JSON object with these fields:
            - location: extracted location (city, country, etc.) or null if not specified
            - date_time: extracted date/time reference or null if current time implied
            - weather_aspect: specific weather aspect (temperature, rain, wind, etc.) or null for general weather
            - query_type: one of "current", "forecast", "historical", "comparison"
            - confidence: confidence score between 0.0 and 1.0
            
            Examples:
            "What's the weather in Paris?" -> {"location": "Paris", "date_time": null, "weather_aspect": null, "query_type": "current", "confidence": 0.9}
            "Will it rain tomorrow in London?" -> {"location": "London", "date_time": "tomorrow", "weather_aspect": "rain", "query_type": "forecast", "confidence": 0.95}
            "Temperature in Tokyo next week" -> {"location": "Tokyo", "date_time": "next week", "weather_aspect": "temperature", "query_type": "forecast", "confidence": 0.9}
            """

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=200
            )

            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            parsed_data = json.loads(content)
            
            return ParsedQuery(
                location=parsed_data.get("location"),
                date_time=parsed_data.get("date_time"),
                weather_aspect=parsed_data.get("weather_aspect"),
                query_type=parsed_data.get("query_type", "current"),
                confidence=parsed_data.get("confidence", 0.5),
                original_query=query
            )

        except Exception as e:
            logger.error(f"Error parsing query with OpenAI: {e}")
            return self._fallback_parse(query)

    def _fallback_parse(self, query: str) -> ParsedQuery:
        """Fallback parsing when OpenAI is not available"""
        query_lower = query.lower()
        
        # Simple keyword-based parsing
        location = None
        date_time = None
        weather_aspect = None
        query_type = "current"
        confidence = 0.3  # Low confidence for fallback

        # Look for time indicators
        if any(word in query_lower for word in ["tomorrow", "next week", "next month", "forecast"]):
            query_type = "forecast"
            if "tomorrow" in query_lower:
                date_time = "tomorrow"
            elif "next week" in query_lower:
                date_time = "next week"

        # Look for weather aspects
        weather_keywords = {
            "temperature": ["temperature", "temp", "hot", "cold", "warm", "cool"],
            "rain": ["rain", "rainy", "precipitation", "shower"],
            "wind": ["wind", "windy", "breeze"],
            "humidity": ["humidity", "humid"],
            "snow": ["snow", "snowy", "blizzard"]
        }
        
        for aspect, keywords in weather_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                weather_aspect = aspect
                break

        # Extract location (very basic - would need more sophisticated NER)
        common_cities = ["london", "paris", "tokyo", "new york", "los angeles", "chicago", "miami"]
        for city in common_cities:
            if city in query_lower:
                location = city.title()
                break

        return ParsedQuery(
            location=location,
            date_time=date_time,
            weather_aspect=weather_aspect,
            query_type=query_type,
            confidence=confidence,
            original_query=query
        )

    async def generate_natural_response(self, parsed_query: ParsedQuery, weather_data: Dict[str, Any]) -> str:
        """Generate a natural language response based on parsed query and weather data"""
        if not self.client:
            return self._fallback_response(parsed_query, weather_data)

        try:
            system_prompt = """
            You are a friendly weather assistant. Generate natural, conversational responses to weather queries.
            Be helpful, concise, and include relevant details. Use the provided weather data to answer accurately.
            """

            user_prompt = f"""
            Original query: "{parsed_query.original_query}"
            Parsed data: {parsed_query.dict()}
            Weather data: {json.dumps(weather_data, default=str)}
            
            Generate a natural response to the user's weather query.
            """

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating natural response: {e}")
            return self._fallback_response(parsed_query, weather_data)

    def _fallback_response(self, parsed_query: ParsedQuery, weather_data: Dict[str, Any]) -> str:
        """Generate a simple response when OpenAI is not available"""
        if not weather_data:
            return "I'm sorry, I couldn't get weather information for that location."
        
        location = weather_data.get("location", "that location")
        temp = weather_data.get("current_weather", {}).get("temperature")
        condition = weather_data.get("conditions", [{}])[0].get("description", "unknown")
        
        if temp is not None:
            return f"The weather in {location} is {condition} with a temperature of {temp}°C."
        else:
            return f"The weather in {location} is {condition}."

    async def health_check(self) -> bool:
        """Check if the NLP service is available"""
        if not self.client:
            return False
        
        try:
            # Test with a simple query
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return bool(response.choices)
        except Exception:
            return False 