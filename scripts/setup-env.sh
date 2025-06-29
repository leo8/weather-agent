#!/bin/bash

# Weather Agent Environment Setup Helper
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌤️  Weather Agent Environment Setup${NC}"
echo "========================================"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << 'EOF'
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
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
else
    echo -e "${YELLOW}ℹ️  .env file already exists${NC}"
    echo ""
fi

echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Edit the .env file with your actual API keys:"
echo "   - Get OpenAI API key from: https://platform.openai.com/api-keys"
echo "   - Get OpenWeatherMap API key from: https://openweathermap.org/api"
echo "   - (Optional) Get Google Calendar API key from: https://console.cloud.google.com/"
echo ""
echo "2. Install dependencies:"
echo "   uv sync"
echo ""
echo "3. Run the application:"
echo "   uv run uvicorn app.main:app --reload"
echo ""
echo -e "${YELLOW}🔒 Remember: Never commit your .env file to git!${NC}" 