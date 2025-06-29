#!/bin/bash

# Weather Agent Deployment Script for Google Cloud Run
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
SERVICE_NAME="weather-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}🌤️  Weather Agent Deployment Script${NC}"
echo "======================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  PROJECT_ID not set. Please set your Google Cloud Project ID:${NC}"
    echo "export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Create secrets if they don't exist
echo -e "${YELLOW}🔐 Setting up secrets in Google Secret Manager...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found. Please create it with your API keys.${NC}"
    exit 1
fi

# Extract API keys from .env file
OPENAI_KEY=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2 | tr -d '"')
OPENWEATHER_KEY=$(grep "^OPENWEATHER_API_KEY=" .env | cut -d'=' -f2 | tr -d '"')

if [ -z "$OPENAI_KEY" ] || [ -z "$OPENWEATHER_KEY" ]; then
    echo -e "${RED}❌ API keys not found in .env file. Please check your configuration.${NC}"
    exit 1
fi

# Create secrets
echo "$OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$OPENAI_KEY" | gcloud secrets versions add openai-api-key --data-file=- --project=$PROJECT_ID

echo "$OPENWEATHER_KEY" | gcloud secrets create openweather-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$OPENWEATHER_KEY" | gcloud secrets versions add openweather-api-key --data-file=- --project=$PROJECT_ID

echo -e "${GREEN}✅ Secrets configured${NC}"

# Build and deploy using Cloud Build
echo -e "${YELLOW}🏗️  Building and deploying with Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml --project=$PROJECT_ID

# Get the service URL
echo -e "${YELLOW}🔍 Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "======================================"
echo -e "${BLUE}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${BLUE}📖 API Docs: ${SERVICE_URL}/docs${NC}"
echo -e "${BLUE}🔍 Health Check: ${SERVICE_URL}/health${NC}"
echo ""
echo -e "${YELLOW}💡 Test your API:${NC}"
echo "curl ${SERVICE_URL}/health"
echo ""
echo -e "${YELLOW}📱 Frontend URL:${NC}"
echo "You can access the frontend at: ${SERVICE_URL}"
echo ""
echo -e "${GREEN}🚀 Your Weather Agent is now live and ready for interviews!${NC}" 