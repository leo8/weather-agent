# 🌤️ Weather Agent

A sophisticated natural language weather agent with Google Calendar integration, built for AI Engineer recruitment demonstration.

## 🎯 Project Overview

This weather agent understands natural language weather queries and provides intelligent responses using live weather data. It demonstrates modern Python backend development, API integration, natural language processing, and cloud deployment practices.

### Key Features
- 🧠 **Natural Language Processing**: Understands complex weather queries using OpenAI GPT
- 🌍 **Live Weather Data**: Real-time weather information from OpenWeatherMap API
- 📅 **Calendar Integration**: Google Calendar utilities for weather-aware scheduling
- 🚀 **Modern Architecture**: FastAPI with async support, automatic OpenAPI docs
- ☁️ **Cloud Deployment**: Production-ready deployment on Google Cloud Run
- 🔒 **Enterprise Security**: Google Secret Manager for secure API key management
- 🧪 **Comprehensive Testing**: 100% test coverage with pytest and async testing

### Example Queries
- *"What's the weather in New York?"*
- *"Should I bring an umbrella to my meeting in SF tomorrow?"*
- *"Is it good weather for a picnic in Central Park this weekend?"*
- *"Will it rain during my outdoor events today?"*

## 🏗️ Architecture & Tech Stack

### Core Technologies
- **Python 3.11+**: Modern Python with async/await support
- **FastAPI**: High-performance web framework with automatic OpenAPI docs
- **OpenAI GPT**: Advanced natural language understanding
- **OpenWeatherMap API**: Reliable weather data source  
- **Google Calendar API**: Calendar integration utilities
- **UV**: Modern, fast Python dependency management
- **pytest**: Comprehensive testing framework
- **Google Cloud Run**: Serverless container deployment
- **Google Secret Manager**: Secure API key management

### Architecture Decisions

**Why FastAPI over Flask/Django?**
- Automatic OpenAPI documentation generation
- Modern async support out of the box
- Excellent type hints integration with Pydantic
- Built-in request validation and serialization

**Why OpenAI GPT for NLP?**
- Robust natural language understanding for complex queries
- Quick development and reliable results
- Handles edge cases and ambiguous queries gracefully
- Battle-tested for production use

**Why UV for dependency management?**
- 10-100x faster than pip
- Modern approach built in Rust
- Single tool for all dependency operations
- Growing industry adoption

**Why Google Cloud Run?**
- Serverless containers with enterprise reliability
- Pay-per-use pricing model
- Fast cold starts (<1 second)
- Seamless integration with other Google Cloud services

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- Google Cloud CLI (for deployment)
- Required API keys:
  - OpenAI API key
  - OpenWeatherMap API key
  - Google Calendar API credentials (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/leo8/weather-agent.git
   cd weather-agent
   ```

2. **Install dependencies**
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install project dependencies
   uv sync
   ```

3. **Environment configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys
   nano .env
   ```

   Required environment variables:
   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   OPENWEATHER_API_KEY=your-openweather-key-here
   GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json  # Optional
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

4. **Run the application**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Web Interface: http://localhost:8000
   - Health Check: http://localhost:8000/health

## 📖 API Documentation

### Core Endpoints

#### Natural Language Query
```http
POST /query/
Content-Type: application/json

{
  "query": "What's the weather like in Paris tomorrow?"
}
```

#### Direct Weather Lookup
```http
GET /weather/current?location=London&units=metric
```

#### Weather Forecast
```http
GET /weather/forecast?location=Tokyo&days=5
```

#### Calendar Integration
```http
POST /calendar/weather-check
Content-Type: application/json

{
  "date": "2024-01-15",
  "location": "San Francisco"
}
```

### Response Format
```json
{
  "status": "success",
  "data": {
    "location": "Paris, FR",
    "current": {
      "temperature": 18.5,
      "condition": "Partly cloudy",
      "humidity": 65,
      "wind_speed": 12.5
    },
    "response": "Tomorrow in Paris will be partly cloudy with a high of 18°C. Perfect weather for outdoor activities!"
  }
}
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_weather_api.py -v

# Run integration tests
uv run pytest tests/test_integration.py -v
```

### Test Coverage
- **Unit Tests**: Individual service and utility functions
- **Integration Tests**: End-to-end API workflows
- **Error Handling**: Network failures, invalid inputs, API limits
- **Security Tests**: Input validation, authentication
- **Performance Tests**: Response times, concurrent requests

## 🚀 Deployment

### Google Cloud Run Deployment

#### 1. Prerequisites Setup
```bash
# Set project variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### 2. Create Secrets
```bash
# Store API keys in Secret Manager
echo "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo "your-openweather-key" | gcloud secrets create openweather-api-key --data-file=-

# Verify secrets
gcloud secrets list
```

#### 3. Deploy Application
```bash
# Using the deployment script
./deploy.sh

# Or manual deployment
gcloud builds submit --config cloudbuild.yaml
```

### CI/CD Pipeline Setup

#### 1. Infrastructure Setup
```bash
# Set GitHub repository information
export GITHUB_REPO_OWNER="your-username"
export GITHUB_REPO_NAME="weather-agent"

# Run automated setup
./setup-cicd.sh
```

#### 2. GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `GCP_SA_KEY`: Service account key JSON (generated by setup script)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key

#### 3. Deployment Workflow

```bash
# Feature development
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
# → Triggers tests only

# Production deployment
git checkout main
git merge feature/new-feature
git push origin main
# → Triggers tests + deployment to production
```

## 🔍 Monitoring & Troubleshooting

### Health Checks
```bash
# Local
curl http://localhost:8000/health

# Production
curl https://your-service-url/health
```

### View Logs
```bash
# Local development
# Logs appear in terminal

# Production logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=weather-agent" --limit=50
```

### Common Issues

#### 1. API Key Issues
- Verify secrets are created: `gcloud secrets list`
- Check service account permissions
- Ensure API keys are valid and have sufficient quota

#### 2. Build Failures
- Check `cloudbuild.yaml` syntax
- Verify all dependencies in `pyproject.toml`
- Check Docker build context with `.dockerignore`

#### 3. Permission Errors
```bash
# Re-run permission setup
./setup-cicd.sh

# Check service account permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT
```

## 🔒 Security

### API Key Management
- ✅ Secrets stored in Google Secret Manager
- ✅ Never committed to version control
- ✅ Least-privilege service account access
- ✅ Regular key rotation recommended

### Application Security
- ✅ Input validation with Pydantic models
- ✅ CORS configuration for frontend integration
- ✅ Rate limiting protection
- ✅ HTTPS enforcement (Cloud Run default)
- ✅ Error handling without information disclosure

### Development Security
- ✅ Comprehensive `.gitignore` for sensitive files
- ✅ Branch protection rules
- ✅ Required PR reviews for main branch
- ✅ Automated dependency security updates

## 📂 Project Structure

```
weather-agent/
├── app/                          # Main application
│   ├── main.py                   # FastAPI application entry point
│   ├── models/                   # Pydantic data models
│   │   ├── weather.py           # Weather-related models
│   │   └── nlp.py               # NLP request/response models
│   ├── routers/                  # API route handlers
│   │   ├── weather.py           # Weather endpoints
│   │   ├── nlp.py               # Natural language processing
│   │   └── calendar.py          # Calendar integration
│   ├── services/                 # Business logic
│   │   ├── weather_service.py   # Weather API integration
│   │   ├── nlp_service.py       # OpenAI integration
│   │   └── calendar_service.py  # Google Calendar utilities
│   └── utils/                    # Utility functions
├── tests/                        # Test suite
│   ├── test_weather_api.py      # Weather API tests
│   ├── test_nlp_api.py          # NLP endpoint tests
│   ├── test_calendar_api.py     # Calendar integration tests
│   └── test_integration.py      # End-to-end tests
├── frontend/                     # Simple web interface
│   ├── index.html               # Main web page
│   ├── style.css                # Styling
│   └── script.js                # Frontend logic
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       └── deploy.yml           # CI/CD pipeline
├── Dockerfile                    # Container configuration
├── .dockerignore                # Docker build exclusions
├── cloudbuild.yaml              # Google Cloud Build config
├── pyproject.toml               # Python project configuration
├── uv.lock                      # Dependency lock file
└── README.md                    # This file
```

## 🎯 Performance Metrics

### Response Times
- **Simple weather queries**: < 1 second
- **Complex NLP queries**: 2-5 seconds
- **Calendar integration**: 1-3 seconds
- **Health checks**: < 100ms

### Scalability
- **Concurrent requests**: 100+ (Cloud Run auto-scaling)
- **Memory usage**: < 512MB typical
- **Cold start time**: < 1 second
- **Daily API calls**: 10,000+ (within free tiers)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `uv run pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: https://weather-agent-xxx-uc.a.run.app
- **API Documentation**: https://weather-agent-xxx-uc.a.run.app/docs
- **GitHub Repository**: https://github.com/leo8/weather-agent
- **Issue Tracker**: https://github.com/leo8/weather-agent/issues

## 👤 Author

**Léo Dray**
- GitHub: [@leo8](https://github.com/leo8)
- Project: AI Engineer recruitment demonstration

---
