"""
Data models for the Weather Agent API
"""

from .weather import WeatherQuery, WeatherResponse
from .nlp import NLPQuery, NLPResponse

__all__ = ["WeatherQuery", "WeatherResponse", "NLPQuery", "NLPResponse"] 