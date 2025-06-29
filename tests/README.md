# Tests

Minimal test suite for the Weather Agent API.

## Quick Start

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_health.py

# Run with coverage
uv run pytest --cov=app
```

## Test Structure

- `test_health.py` - Health check endpoints
- `test_weather_api.py` - Weather API functionality  
- `test_nlp_api.py` - Natural language processing
- `test_calendar_api.py` - Calendar integration
- `test_integration.py` - End-to-end workflows

## Test Behavior

Tests are designed to work with or without API keys:
- ✅ **With API keys**: Tests full functionality
- ✅ **Without API keys**: Tests graceful degradation (503 responses)

This ensures tests pass in CI/CD environments without requiring secrets.

## Example Output

```bash
$ uv run pytest -v

tests/test_health.py::test_app_health PASSED
tests/test_weather_api.py::test_current_weather_valid_location PASSED
tests/test_nlp_api.py::test_query_endpoint_basic PASSED
tests/test_integration.py::test_weather_nlp_integration PASSED

4 passed, 0 failed
``` 