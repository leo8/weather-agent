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

# Verify authentication
echo -e "${YELLOW}🔐 Verifying authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 > /dev/null; then
    echo -e "${RED}❌ Not authenticated with gcloud. Please run 'gcloud auth login'${NC}"
    exit 1
fi

# Verify project access
echo -e "${YELLOW}🔍 Verifying project access...${NC}"
if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot access project $PROJECT_ID. Please check project ID and permissions.${NC}"
    exit 1
fi

# Enable APIs
echo -e "${YELLOW}🔧 Enabling APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
gcloud services enable iam.googleapis.com --project=$PROJECT_ID

# Wait for APIs to be enabled
echo -e "${YELLOW}⏳ Waiting for APIs to be fully enabled...${NC}"
sleep 10

# Create service account for GitHub Actions
echo -e "${YELLOW}🔑 Creating service account for GitHub Actions...${NC}"
SA_NAME="github-actions-weather-agent"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account already exists
if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID > /dev/null 2>&1; then
    echo -e "${YELLOW}ℹ️  Service account already exists: $SA_EMAIL${NC}"
else
    echo -e "${YELLOW}📝 Creating new service account: $SA_EMAIL${NC}"
    if ! gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions for Weather Agent" \
        --description="Service account for GitHub Actions CI/CD pipeline" \
        --project=$PROJECT_ID; then
        echo -e "${RED}❌ Failed to create service account. Check permissions.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Service account created successfully${NC}"
    
    # Wait for service account to propagate
    echo -e "${YELLOW}⏳ Waiting for service account to propagate...${NC}"
    sleep 10
fi

# Verify service account exists before proceeding
echo -e "${YELLOW}🔍 Verifying service account exists...${NC}"
if ! gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID > /dev/null 2>&1; then
    echo -e "${RED}❌ Service account verification failed. Cannot proceed.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Service account verified: $SA_EMAIL${NC}"

# Grant necessary permissions
echo -e "${YELLOW}🛡️  Granting permissions...${NC}"

echo "  - Adding Cloud Build Editor role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor" \
    --quiet

echo "  - Adding Cloud Run Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin" \
    --quiet

echo "  - Adding Secret Manager Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.admin" \
    --quiet

echo "  - Adding Service Account User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

echo "  - Adding Storage Admin role (for Container Registry)..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin" \
    --quiet

echo -e "${GREEN}✅ All permissions granted successfully${NC}"

# Create service account key
echo -e "${YELLOW}🗝️  Creating service account key...${NC}"
if [ -f "github-actions-key.json" ]; then
    echo -e "${YELLOW}ℹ️  Removing existing key file...${NC}"
    rm github-actions-key.json
fi

gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Service account key created: github-actions-key.json${NC}"

# Set up Cloud Build triggers (only if repository information is provided)
if [ -n "$REPO_OWNER" ] && [ -n "$REPO_NAME" ]; then
    echo -e "${YELLOW}🚀 Setting up Cloud Build triggers...${NC}"
    echo -e "${YELLOW}ℹ️  Note: You must connect your GitHub repository to Cloud Build first.${NC}"
    echo -e "${YELLOW}   Visit: https://console.cloud.google.com/cloud-build/triggers${NC}"
    echo -e "${YELLOW}   Click 'Connect Repository' and follow the instructions.${NC}"
    echo ""
    
    # Check if we can list repositories (indicates GitHub is connected)
    if gcloud builds triggers list --project=$PROJECT_ID > /dev/null 2>&1; then
        echo -e "${YELLOW}🔗 Attempting to create triggers...${NC}"
        
        # Production trigger (main branch)
        if gcloud builds triggers describe weather-agent-prod --project=$PROJECT_ID > /dev/null 2>&1; then
            echo -e "${YELLOW}ℹ️  Production trigger already exists${NC}"
        else
            echo "  - Creating production trigger..."
            if gcloud builds triggers create github \
                --repo-owner=$REPO_OWNER \
                --repo-name=$REPO_NAME \
                --branch-pattern="^main$" \
                --build-config=cloudbuild-prod.yaml \
                --name="weather-agent-prod" \
                --description="Deploy to production on main branch" \
                --project=$PROJECT_ID 2>/dev/null; then
                echo -e "${GREEN}✅ Production trigger created${NC}"
            else
                echo -e "${YELLOW}⚠️  Failed to create production trigger. You may need to connect GitHub first.${NC}"
            fi
        fi

        # Development trigger (dev branch)
        if gcloud builds triggers describe weather-agent-dev --project=$PROJECT_ID > /dev/null 2>&1; then
            echo -e "${YELLOW}ℹ️  Development trigger already exists${NC}"
        else
            echo "  - Creating development trigger..."
            if gcloud builds triggers create github \
                --repo-owner=$REPO_OWNER \
                --repo-name=$REPO_NAME \
                --branch-pattern="^dev$" \
                --build-config=cloudbuild-dev.yaml \
                --name="weather-agent-dev" \
                --description="Deploy to development on dev branch" \
                --project=$PROJECT_ID 2>/dev/null; then
                echo -e "${GREEN}✅ Development trigger created${NC}"
            else
                echo -e "${YELLOW}⚠️  Failed to create development trigger. You may need to connect GitHub first.${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot access Cloud Build triggers. GitHub may not be connected yet.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Cloud Build triggers (GitHub repo info not provided)${NC}"
    echo "   You can create them manually later or re-run with GITHUB_REPO_OWNER and GITHUB_REPO_NAME set"
fi

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