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
        
        # Generate unique request ID for tracking
        request_id = f"{int(start_time.timestamp() * 1000)}"
        
        logger.info(
            "🤖 Agent processing started",
            extra={
                "request_id": request_id,
                "query": query,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": start_time.isoformat()
            }
        )
        
        try:
            # THINK: Analyze the query and plan actions
            logger.debug(f"🧠 Starting THINK phase", extra={"request_id": request_id})
            thought = await self._think(query, request_id)
            
            logger.info(
                "🧠 THINK phase completed",
                extra={
                    "request_id": request_id,
                    "is_weather_related": thought.is_weather_related,
                    "detected_language": thought.detected_language,
                    "confidence": thought.confidence,
                    "suggested_actions": [action.value for action in thought.suggested_actions],
                    "reasoning": thought.reasoning
                }
            )
            
            # ACT: Execute planned actions based on reasoning
            logger.debug(f"⚡ Starting ACT phase", extra={"request_id": request_id})
            actions = await self._act(thought, request_id)
            
            logger.info(
                "⚡ ACT phase completed",
                extra={
                    "request_id": request_id,
                    "actions_executed": len(actions),
                    "successful_actions": sum(1 for action in actions if action.success),
                    "failed_actions": sum(1 for action in actions if not action.success)
                }
            )
            
            # OBSERVE: Process results and generate final response
            logger.debug(f"👁️ Starting OBSERVE phase", extra={"request_id": request_id})
            observation = await self._observe(thought, actions, request_id)
            
            logger.info(
                "👁️ OBSERVE phase completed",
                extra={
                    "request_id": request_id,
                    "final_language": observation.language,
                    "final_confidence": observation.confidence,
                    "response_length": len(observation.final_response)
                }
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(
                "✅ Agent processing completed successfully",
                extra={
                    "request_id": request_id,
                    "processing_time_ms": processing_time,
                    "total_actions": len(actions),
                    "weather_data_included": bool(self._extract_weather_data(actions))
                }
            )
            
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
            logger.error(
                "❌ Agent processing failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
                },
                exc_info=True
            )
            return await self._fallback_response(query, str(e))

    async def _think(self, query: str, request_id: str = "unknown") -> AgentThought:
        """
        THINK phase: Analyze user query and reason about appropriate actions.
        """
        logger.debug(f"🧠 Analyzing query for reasoning", extra={"request_id": request_id, "query": query})
        
        if not self.client:
            logger.warning(f"🧠 Using fallback thinking (no OpenAI client)", extra={"request_id": request_id})
            return self._fallback_think(query, request_id)

        try:
            logger.debug(f"🧠 Calling GPT-4 for query analysis", extra={"request_id": request_id})
            
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
            
            logger.debug(
                f"🧠 GPT-4 response received",
                extra={
                    "request_id": request_id,
                    "response_length": len(content),
                    "usage_prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "usage_completion_tokens": response.usage.completion_tokens if response.usage else None
                }
            )
            
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

            thought_result = AgentThought(
                is_weather_related=thought_data.get("is_weather_related", False),
                detected_language=thought_data.get("detected_language", "en"),
                confidence=thought_data.get("confidence", 0.5),
                reasoning=thought_data.get("reasoning", ""),
                suggested_actions=suggested_actions,
                parsed_query=parsed_query
            )
            
            # Log the actual thought process for observability
            logger.info(
                f"🧠 THINK: {thought_result.reasoning}",
                extra={
                    "request_id": request_id,
                    "weather_related": thought_result.is_weather_related,
                    "language": thought_result.detected_language,
                    "confidence": thought_result.confidence,
                    "location": parsed_query.location if parsed_query else None,
                    "query_type": parsed_query.query_type if parsed_query else "other",
                    "planned_actions": [action.value for action in suggested_actions]
                }
            )
            
            return thought_result

        except Exception as e:
            logger.error(
                f"🧠 Error in thinking phase, falling back",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True
            )
            return self._fallback_think(query, request_id)

    async def _act(self, thought: AgentThought, request_id: str = "unknown") -> List[AgentAction]:
        """
        ACT phase: Execute the actions determined in the thinking phase.
        """
        logger.info(
            f"⚡ ACT: Executing {len(thought.suggested_actions)} actions: {[action.value for action in thought.suggested_actions]}",
            extra={
                "request_id": request_id,
                "actions_to_execute": [action.value for action in thought.suggested_actions]
            }
        )
        
        actions = []
        
        for i, action_type in enumerate(thought.suggested_actions):
            action_start_time = datetime.now()
            
            try:
                logger.debug(
                    f"⚡ Executing action {i+1}/{len(thought.suggested_actions)}: {action_type.value}",
                    extra={"request_id": request_id, "action_type": action_type.value}
                )
                
                if action_type == ActionType.GET_CURRENT_WEATHER:
                    if thought.parsed_query and thought.parsed_query.location:
                        logger.debug(
                            f"🌤️ Calling weather API for current weather",
                            extra={"request_id": request_id, "location": thought.parsed_query.location}
                        )
                        
                        weather_data = await self.weather_service.get_current_weather(
                            thought.parsed_query.location
                        )
                        
                        action_result = AgentAction(
                            action_type=action_type,
                            success=True,
                            data=weather_data.model_dump() if weather_data else None
                        )
                        
                        # Extract key weather details for logging
                        temp = None
                        condition = "unknown"
                        if weather_data and hasattr(weather_data, 'current_weather'):
                            temp = weather_data.current_weather.temperature
                        if weather_data and hasattr(weather_data, 'conditions') and weather_data.conditions:
                            condition = weather_data.conditions[0].description
                        
                        logger.info(
                            f"🌤️ Weather API → Current weather for {thought.parsed_query.location}: {temp}°C, {condition}",
                            extra={
                                "request_id": request_id,
                                "location": thought.parsed_query.location,
                                "temperature": temp,
                                "condition": condition,
                                "api_call_time_ms": (datetime.now() - action_start_time).total_seconds() * 1000
                            }
                        )
                    else:
                        action_result = AgentAction(
                            action_type=action_type,
                            success=False,
                            error="No location specified for weather query"
                        )
                        logger.warning(
                            f"🌤️ Current weather request failed - no location",
                            extra={"request_id": request_id}
                        )
                
                elif action_type == ActionType.GET_WEATHER_FORECAST:
                    if thought.parsed_query and thought.parsed_query.location:
                        logger.debug(
                            f"🔮 Calling weather API for forecast",
                            extra={"request_id": request_id, "location": thought.parsed_query.location}
                        )
                        
                        forecast_data = await self.weather_service.get_weather_forecast(
                            thought.parsed_query.location
                        )
                        
                        action_result = AgentAction(
                            action_type=action_type,
                            success=True,
                            data=forecast_data.model_dump() if forecast_data else None
                        )
                        
                        # Extract forecast summary for logging
                        forecast_summary = "No forecast data"
                        if forecast_data and hasattr(forecast_data, 'forecast') and forecast_data.forecast:
                            forecast_summary = f"{len(forecast_data.forecast)} days forecast available"
                        
                        logger.info(
                            f"🔮 Weather API → Forecast for {thought.parsed_query.location}: {forecast_summary}",
                            extra={
                                "request_id": request_id,
                                "location": thought.parsed_query.location,
                                "forecast_days": len(forecast_data.forecast) if forecast_data and hasattr(forecast_data, 'forecast') else 0,
                                "api_call_time_ms": (datetime.now() - action_start_time).total_seconds() * 1000
                            }
                        )
                    else:
                        action_result = AgentAction(
                            action_type=action_type,
                            success=False,
                            error="No location specified for forecast query"
                        )
                        logger.warning(
                            f"🔮 Forecast request failed - no location",
                            extra={"request_id": request_id}
                        )
                
                elif action_type == ActionType.DIRECT_RESPONSE:
                    # No external action needed, will be handled in observation
                    action_result = AgentAction(
                        action_type=action_type,
                        success=True,
                        data={"ready_for_direct_response": True}
                    )
                    logger.info(
                        f"💬 No API calls needed → Preparing direct conversational response",
                        extra={"request_id": request_id}
                    )
                
                else:  # NO_ACTION
                    action_result = AgentAction(
                        action_type=action_type,
                        success=True,
                        data={"no_action_taken": True}
                    )
                    logger.debug(
                        f"⏸️ No action taken as planned",
                        extra={"request_id": request_id}
                    )
                
                actions.append(action_result)
                    
            except WeatherServiceUnavailable as e:
                action_result = AgentAction(
                    action_type=action_type,
                    success=False,
                    error="Weather service unavailable"
                )
                actions.append(action_result)
                logger.error(
                    f"🌤️ Weather service unavailable",
                    extra={"request_id": request_id, "action_type": action_type.value, "error": str(e)}
                )
                
            except WeatherLocationNotFound as e:
                action_result = AgentAction(
                    action_type=action_type,
                    success=False,
                    error="Location not found"
                )
                actions.append(action_result)
                logger.error(
                    f"🌤️ Weather location not found",
                    extra={"request_id": request_id, "action_type": action_type.value, "location": thought.parsed_query.location if thought.parsed_query else None}
                )
                
            except Exception as e:
                action_result = AgentAction(
                    action_type=action_type,
                    success=False,
                    error=str(e)
                )
                actions.append(action_result)
                logger.error(
                    f"⚡ Action execution failed",
                    extra={"request_id": request_id, "action_type": action_type.value, "error": str(e)},
                    exc_info=True
                )
        
        successful_actions = sum(1 for action in actions if action.success)
        failed_actions = sum(1 for action in actions if not action.success)
        
        logger.info(
            f"⚡ ACT Complete → {successful_actions}/{len(actions)} actions successful",
            extra={
                "request_id": request_id,
                "total_actions": len(actions),
                "successful_actions": successful_actions,
                "failed_actions": failed_actions
            }
        )
        
        return actions

    async def _observe(self, thought: AgentThought, actions: List[AgentAction], request_id: str = "unknown") -> AgentObservation:
        """
        OBSERVE phase: Process action results and generate final response.
        """
        logger.info(
            f"👁️ OBSERVE: Generating {thought.detected_language} response from {len(actions)} action results",
            extra={
                "request_id": request_id,
                "target_language": thought.detected_language,
                "actions_to_analyze": len(actions),
                "successful_actions": sum(1 for action in actions if action.success)
            }
        )
        
        if not self.client:
            logger.warning(f"👁️ Using fallback observation (no OpenAI client)", extra={"request_id": request_id})
            return self._fallback_observe(thought, actions, request_id)

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

            logger.debug(
                f"👁️ Calling GPT-4 for response generation",
                extra={
                    "request_id": request_id,
                    "context_size": len(str(context)),
                    "successful_actions": sum(1 for action in actions if action.success)
                }
            )

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
            
            logger.info(
                f"👁️ OBSERVE Complete → Final response: \"{final_response[:100]}{'...' if len(final_response) > 100 else ''}\"",
                extra={
                    "request_id": request_id,
                    "full_response": final_response,
                    "response_length": len(final_response),
                    "target_language": thought.detected_language,
                    "usage_prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "usage_completion_tokens": response.usage.completion_tokens if response.usage else None
                }
            )
            
            return AgentObservation(
                needs_more_actions=False,
                final_response=final_response,
                confidence=min(thought.confidence + 0.1, 1.0),
                language=thought.detected_language
            )

        except Exception as e:
            logger.error(
                f"👁️ Error in observation phase, falling back",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True
            )
            return self._fallback_observe(thought, actions, request_id)

    def _fallback_think(self, query: str, request_id: str = "unknown") -> AgentThought:
        """Fallback thinking when OpenAI is not available"""
        logger.debug(f"🧠 Using rule-based fallback thinking", extra={"request_id": request_id})
        
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
        
        logger.info(
            f"🧠 THINK (Fallback): Query seems {'weather-related' if is_weather_related else 'conversational'} in {detected_language}",
            extra={
                "request_id": request_id,
                "weather_related": is_weather_related,
                "language": detected_language,
                "actions": [action.value for action in suggested_actions],
                "reasoning": "Rule-based analysis (OpenAI unavailable)"
            }
        )
        
        return AgentThought(
            is_weather_related=is_weather_related,
            detected_language=detected_language,
            confidence=0.4,  # Lower confidence for fallback
            reasoning="Fallback analysis - limited reasoning capabilities",
            suggested_actions=suggested_actions,
            parsed_query=None
        )

    def _fallback_observe(self, thought: AgentThought, actions: List[AgentAction], request_id: str = "unknown") -> AgentObservation:
        """Fallback observation when OpenAI is not available"""
        logger.info(f"👁️ OBSERVE (Fallback): Using template-based response generation", extra={"request_id": request_id})
        
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
                    
                logger.info(
                    f"👁️ OBSERVE (Fallback) → Weather response: \"{final_response}\"",
                    extra={"request_id": request_id, "location": location, "temperature": temp, "language": thought.detected_language}
                )
            else:
                if thought.detected_language == "fr":
                    final_response = "Désolé, je n'ai pas pu obtenir les informations météo."
                elif thought.detected_language == "es":
                    final_response = "Lo siento, no pude obtener la información del tiempo."
                else:
                    final_response = "Sorry, I couldn't get the weather information."
                    
                logger.info(
                    f"👁️ OBSERVE (Fallback) → No weather data: \"{final_response}\"",
                    extra={"request_id": request_id, "reason": "no_weather_data", "language": thought.detected_language}
                )
        else:
            # Non-weather query
            if thought.detected_language == "fr":
                final_response = "Bonjour! Je suis un assistant météo. Comment puis-je vous aider avec la météo?"
            elif thought.detected_language == "es":
                final_response = "¡Hola! Soy un asistente del tiempo. ¿Cómo puedo ayudarte con el clima?"
            else:
                final_response = "Hello! I'm a weather assistant. How can I help you with weather information?"
                
            logger.info(
                f"👁️ OBSERVE (Fallback) → Conversational response: \"{final_response}\"",
                extra={"request_id": request_id, "language": thought.detected_language}
            )
        
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
        logger.error(f"❌ Generating fallback response due to error: {error}")
        
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
        logger.debug("🩺 Running agent health check")
        
        if not self.client:
            logger.warning("🩺 Health check failed - no OpenAI client")
            return False
        
        try:
            # Test with a simple query
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            is_healthy = bool(response.choices)
            logger.info(f"🩺 Agent health check {'passed' if is_healthy else 'failed'}")
            return is_healthy
            
        except Exception as e:
            logger.error(f"🩺 Health check failed with error: {e}")
            return False 