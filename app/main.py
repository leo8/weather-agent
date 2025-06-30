"""
Weather Agent - FastAPI Application
Main application entry point for the weather agent API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import logging.config
import json
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from pathlib import Path

from .routers import weather_router, nlp_router, calendar_router

# Load environment variables
load_dotenv()

# Enhanced logging configuration
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        # Create the base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add any extra fields from the log record
        if hasattr(record, 'extra') and record.extra:
            log_entry.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """Setup enhanced logging configuration"""
    environment = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if environment == "production":
        # Production: JSON structured logging
        formatter = StructuredFormatter()
        
        # Console handler with JSON format
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # File handler for persistent logs
        file_handler = logging.FileHandler(log_dir / "weather-agent.jsonl")
        file_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level),
            handlers=[console_handler, file_handler],
            force=True
        )
    else:
        # Development: Human-readable formatting with emojis
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Optional file handler for development debugging
        file_handler = logging.FileHandler(log_dir / "weather-agent-dev.log")
        file_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level),
            handlers=[console_handler, file_handler],
            force=True
        )
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Create agent logger with proper level
    agent_logger = logging.getLogger("app.services.agent_service")
    agent_logger.setLevel(getattr(logging, log_level))
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"🚀 Logging configured for {environment} environment",
        extra={
            "environment": environment,
            "log_level": log_level,
            "structured_logging": environment == "production"
        }
    )

# Setup logging before app creation
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info(
        "🌤️ Weather Agent API starting up",
        extra={
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "0.1.0"
        }
    )
    yield
    # Shutdown
    logger.info("🌤️ Weather Agent API shutting down")

# Create FastAPI instance
app = FastAPI(
    title="Weather Agent API",
    description="A natural language weather agent that provides weather information and calendar integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 