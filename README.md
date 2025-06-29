# Weather Agent 🌤️

A natural language weather agent built with FastAPI that understands weather queries and provides calendar integration. Ask questions like "What's the weather in Paris?" or "Will it rain tomorrow in Tokyo?" and get intelligent, conversational responses.

## ✨ Features

- 🧠 **Natural Language Processing**: Ask weather questions in plain English
- 🌍 **Real-time Weather Data**: Current conditions and forecasts from OpenWeatherMap
- 📅 **Calendar Integration**: Weather-based recommendations for your events
- ⚡ **Fast & Modern**: Built with FastAPI, async/await, and modern Python practices
- 📖 **Auto-generated Documentation**: Interactive API docs with Swagger UI
- 🔒 **Secure**: Proper secrets management and environment configuration
- 🚀 **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🌐 Live Demo

- **Production**: https://weather-agent-xxx-uc.a.run.app
- **API Documentation**: https://weather-agent-xxx-uc.a.run.app/docs
- **Health Check**: https://weather-agent-xxx-uc.a.run.app/health

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **[UV](https://docs.astral.sh/uv/)** - Modern Python dependency management
- **API Keys** (see setup instructions below)

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd weather-agent

# Install dependencies with UV
uv sync
```

This will automatically:
- Create a `.venv` virtual environment
- Install all dependencies from `pyproject.toml`

### 2. API Keys Setup

You'll need to obtain API keys from these services:

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

#### OpenWeatherMap API Key
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to API Keys section in your account
4. Copy your API key

#### Google Calendar API Key (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Calendar API
4. Create credentials (API Key)
5. Copy the API key

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual API keys:

```env
# OpenAI API Configuration
OPENAI_API_KEY="sk-your-openai-key-here"

# Weather API Configuration
OPENWEATHER_API_KEY="your-openweather-key-here"

# Google Calendar API Configuration (Optional)
GOOGLE_CALENDAR_API_KEY="your-google-calendar-key-here"

# Google Cloud Platform Configuration (Optional)
GCP_PROJECT_ID="your-gcp-project-id"

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**⚠️ Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

### 4. Run the Application

```bash
# Method 1: Using UV (recommended)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Activate environment manually
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc

## 🧪 Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Natural Language Queries
```bash
# Basic weather query
curl -X POST "http://localhost:8000/query/" \
     -H "Content-Type: application/json" \
     -d '{"query": "What'\''s the weather in London today?"}'

# Forecast query
curl -X POST "http://localhost:8000/query/" \
     -H "Content-Type: application/json" \
     -d '{"query": "Will it rain tomorrow in Tokyo?"}'

# Complex query
curl -X POST "http://localhost:8000/query/" \
     -H "Content-Type: application/json" \
     -d '{"query": "Should I bring a jacket to my meeting in San Francisco?"}'
```

### Direct Weather API
```bash
# Current weather
curl "http://localhost:8000/weather/current/Paris"

# 5-day forecast
curl "http://localhost:8000/weather/forecast/London?days=5"
```

### Calendar Integration
```bash
curl -X POST "http://localhost:8000/calendar/weather-check" \
     -H "Content-Type: application/json" \
     -d '{"query": "Should I reschedule my outdoor events this week?"}'
```

## 🏗️ Architecture

### Tech Stack
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **UV**: Lightning-fast Python package manager (10-100x faster than pip)
- **OpenAI GPT**: Natural language understanding and response generation
- **OpenWeatherMap**: Real-time weather data and forecasts
- **Pydantic**: Data validation and serialization
- **Google Cloud Run**: Serverless deployment platform

### Project Structure
```
weather-agent/
├── app/
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic (Weather, NLP, Calendar)
│   ├── routers/         # API endpoints
│   ├── utils/           # Utility functions
│   └── main.py          # FastAPI application
├── frontend/            # Web interface
├── tests/               # Test cases
├── .github/workflows/   # CI/CD pipelines
├── .env                 # Environment variables (not in git)
├── pyproject.toml       # Project dependencies and metadata
├── uv.lock             # Lock file for reproducible builds
├── Dockerfile          # Container configuration
├── cloudbuild*.yaml    # Cloud Build configurations
└── README.md           # This file
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Frontend web interface |
| `GET` | `/api` | API information |
| `GET` | `/health` | Application health check |
| `GET` | `/docs` | Interactive API documentation |
| `POST` | `/query/` | **Main endpoint**: Natural language weather queries |
| `GET` | `/weather/current/{location}` | Current weather for a location |
| `GET` | `/weather/forecast/{location}` | Weather forecast |
| `POST` | `/calendar/weather-check` | Weather recommendations for calendar events |

## 🔧 Development

### Adding Dependencies
```bash
uv add package-name
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run flake8

# Type checking
uv run mypy app/
```

### Running Tests
```bash
uv run pytest tests/ -v
```

## 🚀 Deployment

### Manual Deployment to Google Cloud Run

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Deploy
./deploy.sh
```

### CI/CD Pipeline

This project includes automated CI/CD with GitHub Actions:

#### Branch Strategy
- **`main`**: Production environment (auto-deploys to Cloud Run)
- **`dev`**: Development environment (auto-deploys to Cloud Run dev instance)
- **Feature branches**: Run tests only

#### Setup CI/CD

1. **Set up infrastructure:**
   ```bash
   export GITHUB_REPO_OWNER="your-username"
   export GITHUB_REPO_NAME="weather-agent"
   ./setup-cicd.sh
   ```

2. **Add GitHub Secrets:**
   - `GCP_PROJECT_ID`: Your Google Cloud Project ID
   - `GCP_SA_KEY`: Contents of `github-actions-key.json`
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key

3. **Create branches and deploy:**
   ```bash
   git checkout -b dev
   git checkout -b main
   git push -u origin main
   ```

#### CI/CD Features
- ✅ **Automated testing** on pull requests
- ✅ **Production deployment** on push to `main`
- ✅ **Development deployment** on push to `dev`
- ✅ **Health checks** after deployment
- ✅ **PR comments** with deployment URLs

## 🚨 Troubleshooting

### "API key not found" errors
1. Check that your `.env` file exists in the project root
2. Verify API keys are properly formatted (no extra spaces)
3. Restart the application after changing `.env`

### Weather data not found
1. Verify your OpenWeatherMap API key is active
2. Check location spelling (try major cities first)
3. Check the `/weather/health` endpoint for API status

### NLP not working
1. Verify your OpenAI API key is correct
2. Check you have sufficient API credits
3. Test with simple queries first: "Weather in Paris"

### Import errors
1. Make sure you're in the virtual environment: `source .venv/bin/activate`
2. Reinstall dependencies: `uv sync`

## 📈 Performance

- **Average response time**: 2-5 seconds for natural language queries
- **Weather API**: ~500ms for current conditions
- **NLP processing**: ~2-4 seconds depending on query complexity
- **Forecast queries**: ~1-3 seconds for 5-day forecasts

## 🔐 Security

- API keys stored in environment variables only
- `.env` file excluded from version control
- Google Secret Manager for production secrets
- No sensitive data in logs or responses
- CORS configured for development (update for production)

## 🌟 Example Responses

### Natural Language Query
**Input**: "What's the weather in London today?"

**Response**:
```json
{
  "parsed_query": {
    "location": "London",
    "query_type": "current",
    "confidence": 0.95
  },
  "natural_response": "The weather in London today is quite pleasant. Currently, it is 24.91°C with scattered clouds. The humidity is at 52% and the visibility is good.",
  "weather_data": {
    "location": "London",
    "current_weather": {
      "temperature": 24.91,
      "feels_like": 24.81,
      "humidity": 52
    }
  }
}
```

## 🎯 Next Steps

This weather agent is designed to be extensible. Potential enhancements:

1. **Enhanced Calendar Integration**: Full Google Calendar API implementation
2. **Weather Alerts**: Proactive notifications for severe weather
3. **Location Intelligence**: GPS-based weather queries
4. **Historical Data**: Weather history and trends
5. **Multiple Data Sources**: Weather.com integration
6. **Caching**: Redis for improved performance

---

**Built with ❤️ using modern Python practices and AI**
