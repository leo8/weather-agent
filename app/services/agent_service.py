"""
Intelligent Weather Agent Service

This service implements an intelligent agent that can:
1. Analyze user queries to determine if they're weather-related
2. Detect user language for appropriate responses  
3. Make smart decisions about which tools to use
4. Respond naturally in the user's language

The agent follows a Think → Act → Observe pattern for intelligent behavior.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import asyncio
from pydantic import BaseModel

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from ..models.nlp import ParsedQuery, NLPResponse
from ..services.weather_service import WeatherService, WeatherServiceUnavailable, WeatherLocationNotFound, WeatherServiceError

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions the agent can take"""
    NO_ACTION = "no_action"
    GET_CURRENT_WEATHER = "get_current_weather"
    GET_WEATHER_FORECAST = "get_weather_forecast"
    DIRECT_RESPONSE = "direct_response"


class AgentThought(BaseModel):
    """Result of the agent's thinking phase"""
    is_weather_related: bool
    detected_language: str
    confidence: float
    reasoning: str
    suggested_actions: List[ActionType]
    parsed_query: Optional[ParsedQuery] = None


class AgentAction(BaseModel):
    """Result of an action execution"""
    action_type: ActionType
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentObservation(BaseModel):
    """Result of the agent's observation phase"""
    needs_more_actions: bool
    final_response: str
    confidence: float
    language: str


class WeatherAgentService:
    """
    Intelligent weather agent service.
    
    This service provides intelligent behavior by:
    1. Analyzing queries to determine if they're weather-related
    2. Detecting user language for appropriate responses
    3. Making reasoned decisions about which tools to use
    4. Following an intelligent agent pattern for better user experience
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.weather_service = WeatherService()
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        elif AsyncOpenAI:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI package not installed. Agent capabilities limited.")

    async def process_query(self, query: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> NLPResponse:
        """
        Main entry point for processing user queries with intelligent agent behavior.
        
        Args:
            query: User's natural language query
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            NLPResponse with intelligent reasoning and final answer
        """
        start_time = datetime.now()
        
        try:
            # THINK: Analyze the query and plan actions
            thought = await self._think(query)
            
            # ACT: Execute planned actions based on reasoning
            actions = await self._act(thought)
            
            # OBSERVE: Process results and generate final response
            observation = await self._observe(thought, actions)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return NLPResponse(
                parsed_query=thought.parsed_query or ParsedQuery(
                    location=None,
                    date_time=None,
                    weather_aspect=None,
                    query_type="other",
                    confidence=thought.confidence,
                    original_query=query
                ),
                natural_response=observation.final_response,
                weather_data=self._extract_weather_data(actions),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in agent processing: {e}")
            return await self._fallback_response(query, str(e))

    async def _think(self, query: str) -> AgentThought:
        """
        THINK phase: Analyze user query and reason about appropriate actions.
        
        This phase determines:
        - Whether the query is weather-related
        - What language the user is using
        - What actions should be taken
        - Parse weather-specific information if relevant
        """
        if not self.client:
            return self._fallback_think(query)

        try:
            system_prompt = """
            You are an intelligent weather agent. Analyze the user's query and reason about what actions to take.

            Analyze the query and determine:
            1. Is this query weather-related? (true/false)
            2. What language is the user using? (detect language code like 'en', 'fr', 'es', etc.)
            3. What actions should be taken? Use EXACTLY these action names:
               - "weather_current" for current weather queries
               - "weather_forecast" for future weather queries (tomorrow, next week, etc.)
               - "direct_response" for non-weather queries
               - "no_action" for unclear queries
            4. If weather-related, extract location, time, and specific weather aspects

            Return a JSON object with this structure:
            {
                "is_weather_related": boolean,
                "detected_language": "language_code",
                "confidence": float (0.0-1.0),
                "reasoning": "explanation of your thinking process",
                "suggested_actions": ["action1", "action2"],
                "parsed_query": {
                    "location": "extracted location or null",
                    "date_time": "time reference or null", 
                    "weather_aspect": "specific aspect or null",
                    "query_type": "current/forecast/other"
                }
            }

            Examples:
            - "What's the weather in Paris?" → {"suggested_actions": ["weather_current"]}
            - "Will it rain tomorrow in London?" → {"suggested_actions": ["weather_forecast"]}
            - "¿Lloverá mañana en Madrid?" → {"suggested_actions": ["weather_forecast"]}
            - "Hello, how are you?" → {"suggested_actions": ["direct_response"]}
            """

            response = await self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better reasoning
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            thought_data = json.loads(content)
            
            # Convert suggested actions to ActionType enum
            suggested_actions = []
            for action in thought_data.get("suggested_actions", []):
                if action == "weather_current":
                    suggested_actions.append(ActionType.GET_CURRENT_WEATHER)
                elif action == "weather_forecast":
                    suggested_actions.append(ActionType.GET_WEATHER_FORECAST)
                elif action == "direct_response":
                    suggested_actions.append(ActionType.DIRECT_RESPONSE)
                else:
                    suggested_actions.append(ActionType.NO_ACTION)

            # Create parsed query if weather-related
            parsed_query = None
            if thought_data.get("is_weather_related") and thought_data.get("parsed_query"):
                pq_data = thought_data["parsed_query"]
                parsed_query = ParsedQuery(
                    location=pq_data.get("location"),
                    date_time=pq_data.get("date_time"),
                    weather_aspect=pq_data.get("weather_aspect"),
                    query_type=pq_data.get("query_type", "current"),
                    confidence=thought_data.get("confidence", 0.5),
                    original_query=query
                )

            return AgentThought(
                is_weather_related=thought_data.get("is_weather_related", False),
                detected_language=thought_data.get("detected_language", "en"),
                confidence=thought_data.get("confidence", 0.5),
                reasoning=thought_data.get("reasoning", ""),
                suggested_actions=suggested_actions,
                parsed_query=parsed_query
            )

        except Exception as e:
            logger.error(f"Error in thinking phase: {e}")
            return self._fallback_think(query)

    async def _act(self, thought: AgentThought) -> List[AgentAction]:
        """
        ACT phase: Execute the actions determined in the thinking phase.
        
        Based on the reasoning, this phase will:
        - Call weather APIs if needed
        - Prepare for direct responses
        - Skip unnecessary tool calls
        """
        actions = []
        
        for action_type in thought.suggested_actions:
            try:
                if action_type == ActionType.GET_CURRENT_WEATHER:
                    if thought.parsed_query and thought.parsed_query.location:
                        weather_data = await self.weather_service.get_current_weather(
                            thought.parsed_query.location
                        )
                        actions.append(AgentAction(
                            action_type=action_type,
                            success=True,
                            data=weather_data.model_dump() if weather_data else None
                        ))
                    else:
                        actions.append(AgentAction(
                            action_type=action_type,
                            success=False,
                            error="No location specified for weather query"
                        ))
                
                elif action_type == ActionType.GET_WEATHER_FORECAST:
                    if thought.parsed_query and thought.parsed_query.location:
                        forecast_data = await self.weather_service.get_weather_forecast(
                            thought.parsed_query.location
                        )
                        actions.append(AgentAction(
                            action_type=action_type,
                            success=True,
                            data=forecast_data.model_dump() if forecast_data else None
                        ))
                    else:
                        actions.append(AgentAction(
                            action_type=action_type,
                            success=False,
                            error="No location specified for forecast query"
                        ))
                
                elif action_type == ActionType.DIRECT_RESPONSE:
                    # No external action needed, will be handled in observation
                    actions.append(AgentAction(
                        action_type=action_type,
                        success=True,
                        data={"ready_for_direct_response": True}
                    ))
                
                else:  # NO_ACTION
                    actions.append(AgentAction(
                        action_type=action_type,
                        success=True,
                        data={"no_action_taken": True}
                    ))
                    
            except WeatherServiceUnavailable:
                actions.append(AgentAction(
                    action_type=action_type,
                    success=False,
                    error="Weather service unavailable"
                ))
            except WeatherLocationNotFound:
                actions.append(AgentAction(
                    action_type=action_type,
                    success=False,
                    error="Location not found"
                ))
            except Exception as e:
                logger.error(f"Error executing action {action_type}: {e}")
                actions.append(AgentAction(
                    action_type=action_type,
                    success=False,
                    error=str(e)
                ))
        
        return actions

    async def _observe(self, thought: AgentThought, actions: List[AgentAction]) -> AgentObservation:
        """
        OBSERVE phase: Process action results and generate final response.
        
        This phase:
        - Analyzes the results of actions taken
        - Determines if more actions are needed
        - Generates the final response in the user's language
        """
        if not self.client:
            return self._fallback_observe(thought, actions)

        try:
            # Prepare context for response generation
            context = {
                "original_query": thought.parsed_query.original_query if thought.parsed_query else "",
                "user_language": thought.detected_language,
                "is_weather_related": thought.is_weather_related,
                "reasoning": thought.reasoning,
                "action_results": [
                    {
                        "action": action.action_type.value,
                        "success": action.success,
                        "data": action.data,
                        "error": action.error
                    }
                    for action in actions
                ]
            }

            system_prompt = f"""
            You are a helpful weather assistant. Generate a final response based on:
            1. The user's original query
            2. The reasoning process 
            3. The results of actions taken
            
            CRITICAL REQUIREMENTS:
            - ALWAYS respond in the same language as the user's query (detected language: {thought.detected_language})
            - Be natural and conversational
            - If weather data is available, provide helpful and relevant information
            - If no weather data is available due to errors, explain politely
            - If the query was not weather-related, respond helpfully to their actual question
            
            Language examples:
            - English: "The weather in Paris is sunny with 22°C."
            - French: "Le temps à Paris est ensoleillé avec 22°C."  
            - Spanish: "El tiempo en Madrid es soleado con 22°C."
            """

            user_prompt = f"""
            Context: {json.dumps(context, default=str, ensure_ascii=False)}
            
            Generate a natural, helpful response in the user's language ({thought.detected_language}).
            """

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            final_response = response.choices[0].message.content.strip()
            
            # Determine if more actions are needed (generally no for this implementation)
            needs_more_actions = False
            confidence = min(thought.confidence + 0.1, 1.0)  # Slight confidence boost after successful processing
            
            return AgentObservation(
                needs_more_actions=needs_more_actions,
                final_response=final_response,
                confidence=confidence,
                language=thought.detected_language
            )

        except Exception as e:
            logger.error(f"Error in observation phase: {e}")
            return self._fallback_observe(thought, actions)

    def _fallback_think(self, query: str) -> AgentThought:
        """Fallback thinking when OpenAI is not available"""
        query_lower = query.lower()
        
        # Simple weather detection
        weather_keywords = ["weather", "temperature", "rain", "sunny", "cloudy", "forecast", "wind", "humidity", 
                          "météo", "temps", "pluie", "soleil", "vent", "humidité",  # French
                          "tiempo", "lluvia", "sol", "viento", "humedad"]  # Spanish
        
        is_weather_related = any(keyword in query_lower for keyword in weather_keywords)
        
        # Simple language detection
        detected_language = "en"  # Default
        if any(word in query_lower for word in ["bonjour", "quel", "temps", "météo", "il", "fait"]):
            detected_language = "fr"
        elif any(word in query_lower for word in ["hola", "tiempo", "lluvia", "hace", "será"]):
            detected_language = "es"
        
        suggested_actions = []
        if is_weather_related:
            if any(word in query_lower for word in ["tomorrow", "next", "forecast", "demain", "mañana"]):
                suggested_actions.append(ActionType.GET_WEATHER_FORECAST)
            else:
                suggested_actions.append(ActionType.GET_CURRENT_WEATHER)
        else:
            suggested_actions.append(ActionType.DIRECT_RESPONSE)
        
        return AgentThought(
            is_weather_related=is_weather_related,
            detected_language=detected_language,
            confidence=0.4,  # Lower confidence for fallback
            reasoning="Fallback analysis - limited reasoning capabilities",
            suggested_actions=suggested_actions,
            parsed_query=None
        )

    def _fallback_observe(self, thought: AgentThought, actions: List[AgentAction]) -> AgentObservation:
        """Fallback observation when OpenAI is not available"""
        # Check if we have successful weather data
        weather_data = None
        for action in actions:
            if action.success and action.data:
                # Check for both current weather and forecast data
                data_str = str(action.data)
                if "current_weather" in data_str or "forecast" in data_str:
                    weather_data = action.data
                    break
        
        if thought.is_weather_related:
            if weather_data:
                location = weather_data.get("location", "that location")
                
                # Handle both current weather and forecast data
                temp = None
                condition = "unknown"
                
                if "current_weather" in weather_data:
                    # Current weather data
                    temp = weather_data.get("current_weather", {}).get("temperature")
                    condition = weather_data.get("conditions", [{}])[0].get("description", "unknown")
                elif "forecast" in weather_data:
                    # Forecast data - use first forecast item
                    forecast_items = weather_data.get("forecast", [])
                    if forecast_items:
                        first_item = forecast_items[0]
                        temp = first_item.get("weather_data", {}).get("temperature")
                        condition = first_item.get("conditions", [{}])[0].get("description", "unknown")
                
                # Generate response in detected language
                if thought.detected_language == "fr":
                    final_response = f"Le temps à {location} est {condition} avec {temp}°C."
                elif thought.detected_language == "es": 
                    final_response = f"El tiempo en {location} es {condition} con {temp}°C."
                else:
                    final_response = f"The weather in {location} is {condition} with {temp}°C."
            else:
                if thought.detected_language == "fr":
                    final_response = "Désolé, je n'ai pas pu obtenir les informations météo."
                elif thought.detected_language == "es":
                    final_response = "Lo siento, no pude obtener la información del tiempo."
                else:
                    final_response = "Sorry, I couldn't get the weather information."
        else:
            # Non-weather query
            if thought.detected_language == "fr":
                final_response = "Bonjour! Je suis un assistant météo. Comment puis-je vous aider avec la météo?"
            elif thought.detected_language == "es":
                final_response = "¡Hola! Soy un asistente del tiempo. ¿Cómo puedo ayudarte con el clima?"
            else:
                final_response = "Hello! I'm a weather assistant. How can I help you with weather information?"
        
        return AgentObservation(
            needs_more_actions=False,
            final_response=final_response,
            confidence=0.4,
            language=thought.detected_language
        )

    def _extract_weather_data(self, actions: List[AgentAction]) -> Optional[Dict[str, Any]]:
        """Extract weather data from successful actions"""
        for action in actions:
            if action.success and action.data:
                # Check for both current weather and forecast data
                data_str = str(action.data)
                if "current_weather" in data_str or "forecast" in data_str:
                    return action.data
        return None

    async def _fallback_response(self, query: str, error: str) -> NLPResponse:
        """Generate a fallback response when the entire process fails"""
        return NLPResponse(
            parsed_query=ParsedQuery(
                location=None,
                date_time=None,
                weather_aspect=None,
                query_type="error",
                confidence=0.0,
                original_query=query
            ),
            natural_response="I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            weather_data=None,
            processing_time_ms=0
        )

    async def health_check(self) -> bool:
        """Check if the agent service is available"""
        if not self.client:
            return False
        
        try:
            # Test with a simple query
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            return bool(response.choices)
        except Exception:
            return False 