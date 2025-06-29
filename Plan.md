# Weather Agent Engineering Test - Implementation Plan

## Project Overview
Build a backend agent that understands natural language weather queries using live weather.com data, with Google Calendar integration utilities.

## Architecture Decisions

### Tech Stack Choice

#### **Primary Language: Python**
- **Chosen**: Python
- **Rationale**: Aligns with company tech stack (Python, Node.js, TypeScript)
- **Benefits**: Rich ecosystem for APIs, weather data, and ML integrations

#### **Web Framework: FastAPI**
- **Chosen**: FastAPI
- **Alternatives Considered**: 
  - Flask (lightweight, mature, but requires more setup for modern features)
  - Django REST Framework (full-featured but overkill for this project scope)
- **Rationale**: 
  - Automatic OpenAPI/Swagger documentation generation (great for demo)
  - Modern async support out of the box
  - Excellent type hints integration with Pydantic
  - Built-in request validation
  - Fast development and execution

#### **Natural Language Processing: OpenAI GPT API**
- **Chosen**: OpenAI GPT API
- **Alternatives Considered**: 
  - spaCy + custom logic (no API costs but limited NL understanding)
  - Hugging Face Transformers (local processing but setup complexity)
- **Rationale**: 
  - Quick development and reliable results
  - Excellent natural language understanding for complex queries
  - Battle-tested for production use
  - Allows focus on architecture rather than NLP engineering

#### **Weather Data Source: OpenWeatherMap API (Primary)**
- **Chosen**: OpenWeatherMap API for development, Weather.com API for final implementation
- **Alternatives Considered**: 
  - Weather.com API directly (matches requirements but complex registration)
  - WeatherAPI.com (simpler but not specified in requirements)
- **Rationale**: 
  - OpenWeatherMap: Developer-friendly with good free tier for rapid prototyping
  - Plan to integrate Weather.com API later to meet exact requirements
  - Allows quick MVP development while ensuring final compliance

#### **Testing Framework: pytest + httpx**
- **Chosen**: pytest + httpx
- **Alternatives Considered**: 
  - unittest + requests (standard library but more verbose)
  - pytest + requests (good but no async support)
- **Rationale**: 
  - Modern async testing support for FastAPI
  - Powerful fixtures and parametrization
  - Excellent integration with FastAPI testing patterns
  - Industry standard for Python API testing

#### **Dependency Management: UV**
- **Chosen**: UV (modern Python dependency management)
- **Alternatives Considered**: 
  - pip + requirements.txt (traditional but slower)
  - Poetry (good but more complex setup)
  - Pipenv (mature but slower than UV)
- **Rationale**: 
  - **Extremely fast**: 10-100x faster than pip
  - **Modern approach**: Built in Rust, designed for performance
  - **Simple workflow**: Single tool for dependency management
  - **Industry adoption**: Growing rapidly in the Python ecosystem
  - **Professional edge**: Shows awareness of modern Python tooling

#### **Calendar Integration: Google API Client Library**
- **Chosen**: Official Google API Client Library (google-api-python-client)
- **Alternatives Considered**: 
  - Manual requests approach (lightweight but more work)
  - Specialized third-party libraries (simpler but less reliable)
- **Rationale**: 
  - Official Google library ensures reliability and feature completeness
  - Well-documented and maintained
  - Required for extensible integration during interview
  - Comprehensive error handling and authentication support

#### **Interface & Documentation**
- **Chosen**: REST API + FastAPI auto-generated docs + simple web demo
- **Benefits**: 
  - FastAPI automatically generates interactive OpenAPI documentation
  - Easy to test and demonstrate during interview
  - Professional API documentation without extra work

#### **Version Control & Repository: GitHub**
- **Chosen**: GitHub
- **Benefits**: 
  - Industry standard for professional development
  - Integration with Google Cloud Build for CI/CD
  - Portfolio visibility for potential employers
  - Issue tracking and project management
  - Professional development workflow demonstration

#### **Security & Secrets Management: Google Secret Manager**
- **Chosen**: Google Secret Manager + Environment Variables
- **Alternatives Considered**: 
  - Plain environment variables (simple but less secure)
  - Local .env files (development only, not production-safe)
  - GitHub Secrets (good for CI/CD but not runtime)
- **Rationale**: 
  - **Enterprise-grade security**: Demonstrates understanding of production security
  - **GCP integration**: Seamless with Cloud Run
  - **Audit trails**: Secret access logging and versioning
  - **Runtime security**: Secrets never stored in code or images
- **Implementation**: 
  - Store API keys (OpenAI, Weather, Google Calendar) in Secret Manager
  - Use IAM roles for secure access from Cloud Run
  - Environment variables for non-sensitive configuration

#### **Deployment Platform: Google Cloud Run**
- **Chosen**: Google Cloud Run
- **Alternatives Considered**: 
  - Railway (simple deployment, good Python support, but less sophisticated)
  - Render (free tier available, but cold start limitations)
  - Heroku (mature platform but no free tier, expensive for demos)
  - Vercel (great DX but limited for full Python apps)
- **Rationale**: 
  - **Leverages GCP expertise**: Demonstrates enterprise-grade cloud skills
  - **Serverless containers**: Modern, cloud-native approach shows technical sophistication
  - **Cost-effective**: Pay-per-use pricing, likely free for demo usage
  - **Professional grade**: Enterprise reliability and performance
  - **Fast cold starts**: Sub-second container startup for demos
  - **GitHub integration**: Easy CI/CD setup with Cloud Build
  - **Differentiator**: Most candidates use simpler platforms, this shows advanced skills
- **Implementation**: Containerized FastAPI app with Docker, deployed via Cloud Build from GitHub

### Project Structure
```
weather-agent/
├── app/
│   ├── routers/
│   ├── services/
│   ├── utils/
│   ├── models/
│   └── main.py
├── tests/
├── frontend/ (simple demo interface)
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── cloudbuild.yaml
├── pyproject.toml (UV dependency management)
├── uv.lock
├── README.md
└── .env.example (for local development only)
```

## Implementation Steps

### Phase 1: Project Setup & Foundation (Day 1)
1. **Initialize Project**
   - Create GitHub repository (public for portfolio visibility)
   - Set up Python project with UV (modern dependency management)
   - Configure black, flake8, mypy for code quality
   - Create comprehensive .gitignore (Python, IDE, environment files)
   - Set up basic FastAPI server
   - Create environment configuration with python-dotenv
   - Create Dockerfile and .dockerignore for Cloud Run deployment
   - Initialize proper commit structure and README

2. **Weather Data Integration**
   - Research weather.com API (or alternatives like OpenWeatherMap)
   - Set up API credentials
   - Create weather service module
   - Implement basic weather data fetching
   - Test with different locations

3. **Basic API Structure**
   - Create `/weather` endpoint with FastAPI
   - Implement basic query parsing with Pydantic models
   - Set up error handling middleware
   - Add request logging with Python logging

### Phase 2: Natural Language Processing (Day 2)
4. **NLP Integration**
   - Set up OpenAI API integration
   - Design prompt engineering for weather queries
   - Create query parser that extracts:
     - Location
     - Time/date
     - Weather aspect (temperature, rain, etc.)
   - Handle ambiguous queries

5. **Query Processing Pipeline**
   - Parse natural language input
   - Extract structured data (location, time, weather type)
   - Fetch relevant weather data
   - Format human-readable response

### Phase 3: Google Calendar Integration (Day 2-3)
6. **Calendar Utils Development**
   - Set up Google Calendar API
   - Create authentication flow
   - Implement utility functions:
     - Get events for date range
     - Check for outdoor events
     - Suggest weather-appropriate scheduling
   - Design extensible interface for interview

7. **Weather-Calendar Features**
   - "Should I reschedule my outdoor meeting?"
   - "What's the weather for my events tomorrow?"
   - Event weather alerts

### Phase 4: Interface & User Experience (Day 3)
8. **API Endpoints**
   - `POST /query` - Main natural language endpoint
   - `GET /weather/:location` - Direct weather lookup
   - `POST /calendar/weather-check` - Calendar integration demo
   - `GET /health` - Health check

9. **Simple Frontend**
   - Basic HTML/CSS/JS interface or FastAPI's built-in docs
   - Chat-like interface for natural language queries
   - Display weather data visually
   - Demo calendar integration

### Phase 5: Testing & Quality (Day 3-4)
10. **Comprehensive Testing**
    - Unit tests for weather service
    - Integration tests for API endpoints
    - NLP query parsing tests
    - Calendar integration tests
    - Error handling tests

11. **Performance & Reliability**
    - Add caching for weather data
    - Rate limiting
    - Input validation and sanitization
    - Graceful error handling

### Phase 6: Deployment & Documentation (Day 4)
12. **Security & Secrets Setup**
    - Set up Google Secret Manager
    - Store API keys securely (OpenAI, Weather APIs, Google Calendar)
    - Configure IAM roles for Cloud Run service account
    - Create secure environment variable configuration
    - Test local development with secret access

13. **CI/CD & Deployment**
    - Create Cloud Build configuration (cloudbuild.yaml)
    - Set up GitHub integration with Cloud Build triggers
    - Configure automated deployment on main branch push
    - Deploy via Cloud Build from GitHub repository
    - Set up custom domain and SSL (optional)
    - Test live deployment and performance
    - Create test scenarios for demo

14. **Documentation**
    - Complete README.md with:
      - Setup instructions (including secrets configuration)
      - API documentation
      - Architecture decisions
      - Product decisions rationale
      - Security considerations
      - Deployment guide
    - Code comments and docstrings
    - API examples (FastAPI auto-generates OpenAPI docs)

### Phase 7: Video & Presentation (Day 4-5)
15. **Loom Video Preparation**
    - Script the demo flow
    - Prepare test scenarios
    - Practice presentation
    - Record 5-minute demo covering:
      - Product demonstration
      - Codebase walkthrough
      - Key decisions explanation
      - Security and deployment architecture

## Key Product Decisions

### Interface Choice: REST API + Web Demo
- **Rationale**: Flexible for different frontends, easy to test, demonstrates backend skills
- **Alternative considered**: CLI tool (less demonstrable)

### NLP Approach: OpenAI Integration
- **Rationale**: Robust, handles edge cases, faster development
- **Alternative considered**: Custom NLP (time-intensive, lower quality)

### Weather Data Source
- **Primary**: Weather.com API
- **Fallback**: OpenWeatherMap (more developer-friendly)

### Calendar Integration Design
- **Approach**: Utility functions ready for extension
- **Focus**: Demonstrate integration patterns rather than full implementation

## Testing Strategy

### Test Scenarios
1. **Basic Weather Queries**
   - "What's the weather in New York?"
   - "Will it rain tomorrow in London?"
   - "Temperature in Tokyo next week"

2. **Complex Natural Language**
   - "Should I bring an umbrella to my meeting in SF tomorrow?"
   - "Is it good weather for a picnic in Central Park this weekend?"

3. **Calendar Integration**
   - Weather for scheduled events
   - Outdoor activity recommendations

### Success Metrics
- ✅ Handles 90%+ of natural language weather queries
- ✅ Responds within 2-3 seconds
- ✅ Graceful error handling
- ✅ Calendar utilities are extensible
- ✅ Code is clean and well-documented

## Timeline
- **Day 1**: Project setup, weather integration, basic API
- **Day 2**: NLP processing, calendar utils foundation
- **Day 3**: Interface, testing, integration
- **Day 4**: Deployment, documentation, video prep
- **Day 5**: Final testing, video recording, submission

## Security Considerations

### **API Keys & Secrets Management**
- **Never commit secrets**: Use .gitignore for .env files
- **Google Secret Manager**: Production secret storage
- **IAM Best Practices**: Least privilege access for Cloud Run
- **Environment Separation**: Different secrets for dev/prod
- **Audit Logging**: Track secret access and usage

### **Application Security**
- **Input validation**: Pydantic models for all inputs
- **Rate limiting**: Protect against abuse
- **CORS configuration**: Proper frontend integration
- **HTTPS enforcement**: SSL/TLS for all communications
- **Error handling**: Don't expose sensitive information in errors

### **GitHub Security**
- **Public repository**: Safe for portfolio (no secrets)
- **Branch protection**: Require PR reviews for main
- **Dependabot**: Automated security updates
- **GitHub Actions secrets**: For CI/CD pipeline only

## Risk Mitigation
- **Weather API limits**: Implement caching, have backup API
- **NLP complexity**: Start simple, iterate
- **Calendar API complexity**: Focus on utils structure over full implementation
- **Deployment issues**: Test early, have local demo ready
- **Secret management**: Test secret access in development environment
- **GitHub integration**: Set up CI/CD early to catch issues

## Next Steps
1. Start with weather API research and basic setup
2. Create MVP endpoint to validate approach
3. Iterate quickly with user testing
4. Document decisions as you go
