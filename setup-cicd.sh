#!/bin/bash

# Weather Agent CI/CD Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
REPO_OWNER=${GITHUB_REPO_OWNER:-""}
REPO_NAME=${GITHUB_REPO_NAME:-"weather-agent"}

echo -e "${BLUE}🔧 Weather Agent CI/CD Setup${NC}"
echo "================================"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Please set GOOGLE_CLOUD_PROJECT${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Enable APIs
echo -e "${YELLOW}🔧 Enabling APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Create service account for GitHub Actions
echo -e "${YELLOW}🔑 Creating service account for GitHub Actions...${NC}"
SA_NAME="github-actions-weather-agent"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions for Weather Agent" \
    --project=$PROJECT_ID 2>/dev/null || echo "Service account already exists"

# Grant necessary permissions
echo -e "${YELLOW}🛡️  Granting permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# Create service account key
echo -e "${YELLOW}🗝️  Creating service account key...${NC}"
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Service account key created: github-actions-key.json${NC}"

# Set up Cloud Build triggers
echo -e "${YELLOW}🚀 Setting up Cloud Build triggers...${NC}"

# Production trigger (main branch)
gcloud builds triggers create github \
    --repo-owner=$REPO_OWNER \
    --repo-name=$REPO_NAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild-prod.yaml \
    --name="weather-agent-prod" \
    --description="Deploy to production on main branch" \
    --project=$PROJECT_ID 2>/dev/null || echo "Production trigger already exists"

# Development trigger (dev branch)
gcloud builds triggers create github \
    --repo-owner=$REPO_OWNER \
    --repo-name=$REPO_NAME \
    --branch-pattern="^dev$" \
    --build-config=cloudbuild-dev.yaml \
    --name="weather-agent-dev" \
    --description="Deploy to development on dev branch" \
    --project=$PROJECT_ID 2>/dev/null || echo "Development trigger already exists"

echo ""
echo -e "${GREEN}🎉 CI/CD Setup Complete!${NC}"
echo "=========================="
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Add the following secrets to your GitHub repository:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: (contents of github-actions-key.json)"
echo "   - OPENAI_API_KEY: (your OpenAI API key)"
echo "   - OPENWEATHER_API_KEY: (your OpenWeatherMap API key)"
echo ""
echo "2. Create branches:"
echo "   git checkout -b dev"
echo "   git checkout -b main"
echo ""
echo "3. Push to GitHub:"
echo "   git remote add origin https://github.com/$REPO_OWNER/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo -e "${YELLOW}🔒 IMPORTANT: Delete github-actions-key.json after adding to GitHub secrets!${NC}"
echo "rm github-actions-key.json" 