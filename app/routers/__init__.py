"""
API routers for the Weather Agent
"""

from .weather import router as weather_router
from .nlp import router as nlp_router
from .calendar import router as calendar_router

__all__ = ["weather_router", "nlp_router", "calendar_router"] 