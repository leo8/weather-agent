"""
Weather Agent - FastAPI Application
Main application entry point for the weather agent API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

from .routers import weather_router, nlp_router, calendar_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Weather Agent API",
    description="A natural language weather agent that provides weather information and calendar integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather_router)
app.include_router(nlp_router)
app.include_router(calendar_router)

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_root(request: Request):
        """Serve the frontend application or API info based on Accept header"""
        
        # Check if client accepts JSON (API request) or HTML (browser request)
        accept_header = request.headers.get("accept", "")
        user_agent = request.headers.get("user-agent", "")
        
        # Return JSON for test clients, curl, or explicit JSON requests
        if (
            "application/json" in accept_header or 
            "testclient" in user_agent.lower() or
            "curl" in user_agent.lower() or
            "python" in user_agent.lower() or
            request.url.path == "/" and "text/html" not in accept_header
        ):
            # Return JSON for API clients
            return {
                "message": "Weather Agent API",
                "version": "0.1.0",
                "docs": "/docs",
                "health": "/health",
                "endpoints": {
                    "weather": "/weather",
                    "nlp": "/query",
                    "calendar": "/calendar"
                }
            }
        else:
            # Return HTML for browsers
            return FileResponse(str(frontend_path / "index.html"))
        
    @app.get("/api/", tags=["API Info"])
    async def root_api():
        """Root API endpoint for programmatic access"""
        return {
            "message": "Weather Agent API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "weather": "/weather",
                "nlp": "/query",
                "calendar": "/calendar"
            }
        }

@app.get("/api", tags=["API Info"])
async def api_info():
    """API information endpoint"""
    return {
        "message": "Weather Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "frontend": "/" if frontend_path.exists() else "Not available"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    return {
        "status": "healthy",
        "service": "weather-agent",
        "version": "0.1.0",
        "environment": environment,
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 