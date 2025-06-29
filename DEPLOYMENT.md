# 🚀 Deployment Guide

This guide covers deploying the Weather Agent to Google Cloud Run with automated CI/CD.

## 📋 Prerequisites

- Google Cloud Project with billing enabled
- GitHub repository (public or private)
- Required API keys (OpenAI, OpenWeatherMap)
- Google Cloud CLI installed and authenticated

## 🎯 Deployment Strategy

### Environment Structure
- **Production**: `main` branch → `weather-agent` service
- **Development**: `dev` branch → `weather-agent-dev` service
- **Feature branches**: Tests only (no deployment)

### Resource Configuration
| Environment | Memory | CPU | Max Instances | Machine Type |
|-------------|--------|-----|---------------|--------------|
| Production  | 1Gi    | 1   | 10            | E2_HIGHCPU_8 |
| Development | 512Mi  | 1   | 5             | E2_STANDARD_2 |

## 🛠️ Manual Deployment

### 1. One-time Setup

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# Verify authentication
gcloud auth list
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Create Secrets

```bash
# Create API key secrets
echo "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo "your-openweather-key" | gcloud secrets create openweather-api-key --data-file=-

# Verify secrets
gcloud secrets list
```

### 3. Deploy

```bash
# Deploy using the provided script
./deploy.sh

# Or deploy manually
gcloud builds submit --config cloudbuild.yaml
```

## 🔄 CI/CD Setup

### 1. Infrastructure Setup

```bash
# Set GitHub repository information
export GITHUB_REPO_OWNER="your-username"
export GITHUB_REPO_NAME="weather-agent"
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Run setup script
./setup-cicd.sh
```

This script will:
- Enable required Google Cloud APIs
- Create service account for GitHub Actions
- Grant necessary permissions
- Set up Cloud Build triggers
- Generate service account key

### 2. GitHub Configuration

#### Add Repository Secrets

Go to GitHub → Settings → Secrets and variables → Actions:

1. **`GCP_PROJECT_ID`**: Your Google Cloud Project ID
   ```
   your-project-id
   ```

2. **`GCP_SA_KEY`**: Contents of `github-actions-key.json`
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     ...
   }
   ```

3. **`OPENAI_API_KEY`**: Your OpenAI API key
   ```
   sk-your-openai-key-here
   ```

4. **`OPENWEATHER_API_KEY`**: Your OpenWeatherMap API key
   ```
   your-openweather-key-here
   ```

#### Branch Protection Rules (Recommended)

Go to GitHub → Settings → Branches:

1. **Protect `main` branch**:
   - Require pull request reviews
   - Require status checks to pass (CI tests)
   - Require up-to-date branches

2. **Protect `dev` branch**:
   - Require status checks to pass

### 3. Branch Workflow

```bash
# Create and switch to dev branch
git checkout -b dev
git push -u origin dev

# Create and switch to main branch
git checkout -b main
git push -u origin main

# Set main as default branch (in GitHub settings)
```

### 4. Deployment Workflow

```bash
# Feature development
git checkout dev
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add new feature"
git push origin feature/new-feature
# Create PR to dev → triggers tests

# Development release
git checkout dev
git merge feature/new-feature
git push origin dev
# → Automatically deploys to development environment

# Production release
git checkout main
git merge dev
git push origin main
# → Automatically deploys to production environment
```

## 🔍 Monitoring Deployments

### GitHub Actions

Monitor deployments in GitHub:
- Go to **Actions** tab
- View workflow runs and logs
- Check deployment status and URLs

### Google Cloud Console

Monitor resources:
- **Cloud Run**: Service status and metrics
- **Cloud Build**: Build history and logs
- **Secret Manager**: API key management
- **Logging**: Application logs

### Health Checks

```bash
# Production
curl https://weather-agent-xxx-uc.a.run.app/health

# Development
curl https://weather-agent-dev-xxx-uc.a.run.app/health
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Permission Denied Errors
```bash
# Check service account permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-weather-agent@*"

# Re-run permission setup
./setup-cicd.sh
```

#### 2. Secret Access Issues
```bash
# Check secret permissions
gcloud secrets get-iam-policy openai-api-key

# Grant access to Cloud Run service account
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:$(gcloud run services describe weather-agent --region=us-central1 --format='value(spec.template.spec.serviceAccountName)')@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 3. Build Failures
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Common fixes:
# - Verify Docker context
# - Check cloudbuild.yaml syntax
# - Ensure all dependencies in pyproject.toml
```

#### 4. Service Not Starting
```bash
# Check service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=weather-agent" --limit=50

# Check health endpoint
curl -v https://your-service-url/health
```

### Recovery Procedures

#### Rollback Deployment
```bash
# List revisions
gcloud run revisions list --service=weather-agent --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic weather-agent \
  --to-revisions=weather-agent-00001-abc=100 \
  --region=us-central1
```

#### Emergency Manual Deploy
```bash
# Skip CI/CD and deploy directly
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=weather-agent,_REGION=us-central1
```

## 📊 Performance Monitoring

### Metrics to Watch

1. **Response Time**: Should be < 5 seconds for NLP queries
2. **Error Rate**: Should be < 1%
3. **Memory Usage**: Should stay below 80% of allocated
4. **CPU Usage**: Should stay below 80%

### Alerting Setup

```bash
# Create alerting policy (example)
gcloud alpha monitoring policies create \
  --display-name="Weather Agent High Error Rate" \
  --conditions-display-name="High Error Rate" \
  --conditions-filter='resource.type="cloud_run_revision"' \
  --notification-channels=$NOTIFICATION_CHANNEL_ID
```

## 🔒 Security Best Practices

### API Key Management
- ✅ Store in Google Secret Manager
- ✅ Use least-privilege service accounts
- ✅ Rotate keys regularly
- ✅ Never commit keys to git

### Network Security
- ✅ HTTPS only (Cloud Run default)
- ✅ CORS configured for frontend domain
- ✅ Rate limiting in application
- ✅ Input validation with Pydantic

### Access Control
- ✅ Service account per environment
- ✅ Minimal IAM permissions
- ✅ Protected branches in GitHub
- ✅ Required PR reviews

## 🎯 Next Steps

### Enhancements
1. **Custom Domain**: Set up custom domain with SSL
2. **CDN**: Use Cloud CDN for frontend assets
3. **Database**: Add Cloud SQL for persistent data
4. **Caching**: Implement Redis for API response caching
5. **Monitoring**: Set up comprehensive monitoring with Cloud Operations

### Advanced CI/CD
1. **Blue-Green Deployments**: Zero-downtime deployments
2. **Canary Releases**: Gradual traffic shifting
3. **Integration Tests**: End-to-end testing in CI
4. **Performance Tests**: Load testing in CI pipeline

---

**Need help?** Check the logs first, then GitHub Issues or Google Cloud Support. 