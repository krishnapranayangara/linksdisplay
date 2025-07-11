# GCP Deployment Guide for LinkDisplay

This guide will help you deploy LinkDisplay to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a GCP account with billing enabled
2. **Google Cloud SDK**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install [Docker](https://docs.docker.com/get-docker/) (optional, Cloud Build will handle this)

## Step 1: Set Up GCP Project

1. **Create a new project** (or use existing):
   ```bash
   gcloud projects create linkdisplay-app --name="LinkDisplay"
   ```

2. **Set the project as default**:
   ```bash
   gcloud config set project linkdisplay-app
   ```

3. **Enable billing** for your project in the [GCP Console](https://console.cloud.google.com/billing)

## Step 2: Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable appengine.googleapis.com
```

## Step 3: Authenticate with GCP

```bash
gcloud auth login
gcloud auth application-default login
```

## Step 4: Update Configuration

1. **Edit the deployment script**:
   ```bash
   # Open deploy.sh and replace:
   PROJECT_ID="your-gcp-project-id"
   # with your actual project ID:
   PROJECT_ID="linkdisplay-app"
   ```

2. **Update frontend API URL** (optional):
   - The deployment script will automatically update the API URL
   - Or manually update `frontend/src/App.js` with your backend URL

## Step 5: Deploy to GCP

### Option A: Using the Deployment Script (Recommended)

```bash
./deploy.sh
```

### Option B: Manual Deployment

#### Deploy Backend

```bash
cd backend

# Build and deploy
gcloud builds submit --tag gcr.io/linkdisplay-app/linkdisplay-backend .
gcloud run deploy linkdisplay-backend \
    --image gcr.io/linkdisplay-app/linkdisplay-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production

cd ..
```

#### Deploy Frontend

```bash
cd frontend

# Update API URL (replace with your backend URL)
sed -i.bak "s|http://localhost:3001|https://linkdisplay-backend-xxxxx-uc.a.run.app|g" src/App.js

# Build and deploy
gcloud builds submit --tag gcr.io/linkdisplay-app/linkdisplay-frontend .
gcloud run deploy linkdisplay-frontend \
    --image gcr.io/linkdisplay-app/linkdisplay-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 5

# Restore original API URL
mv src/App.js.bak src/App.js

cd ..
```

## Step 6: Verify Deployment

1. **Check your services**:
   ```bash
   gcloud run services list --region us-central1
   ```

2. **Test the application**:
   - Frontend: Visit the frontend URL provided
   - Backend: Visit the backend URL + `/api/health`

## Step 7: Set Up Custom Domain (Optional)

```bash
# Map a custom domain to your frontend
gcloud run domain-mappings create \
    --service=linkdisplay-frontend \
    --domain=your-domain.com \
    --region=us-central1
```

## Step 8: Environment Variables (Production)

For production, you may want to set additional environment variables:

```bash
gcloud run services update linkdisplay-backend \
    --region us-central1 \
    --set-env-vars \
    SECRET_KEY=your-secret-key,\
    DATABASE_URL=your-database-url,\
    CORS_ORIGINS=https://your-domain.com
```

## Monitoring and Logs

### View Logs

```bash
# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=linkdisplay-backend"

# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=linkdisplay-frontend"
```

### Monitor Performance

- Visit [Cloud Run Console](https://console.cloud.google.com/run)
- Check metrics, logs, and performance

## Cost Optimization

### Free Tier
- Cloud Run: 2 million requests per month
- Cloud Build: 120 build-minutes per day
- Container Registry: 0.5 GB storage

### Cost Control
```bash
# Set maximum instances to control costs
gcloud run services update linkdisplay-backend \
    --region us-central1 \
    --max-instances 5

gcloud run services update linkdisplay-frontend \
    --region us-central1 \
    --max-instances 3
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile syntax and dependencies
2. **Service won't start**: Check logs for errors
3. **CORS issues**: Verify CORS_ORIGINS environment variable
4. **Database connection**: Ensure DATABASE_URL is correct

### Debug Commands

```bash
# Check service status
gcloud run services describe linkdisplay-backend --region us-central1

# View recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Test API endpoint
curl https://linkdisplay-backend-xxxxx-uc.a.run.app/api/health
```

## Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Cloud Run provides HTTPS by default
3. **Authentication**: Consider adding authentication for admin features
4. **CORS**: Configure CORS_ORIGINS properly

## Scaling

### Auto-scaling
Cloud Run automatically scales based on traffic:
- Scales to zero when no traffic
- Scales up to handle load
- Configure max instances to control costs

### Manual Scaling
```bash
# Set minimum instances (prevents cold starts)
gcloud run services update linkdisplay-backend \
    --region us-central1 \
    --min-instances 1
```

## Backup and Recovery

### Database Backup
If using Cloud SQL:
```bash
# Create backup
gcloud sql backups create --instance=your-instance-name

# Restore from backup
gcloud sql instances restore-backup your-instance-name --backup-id=backup-id
```

### Service Rollback
```bash
# List revisions
gcloud run revisions list --service=linkdisplay-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic linkdisplay-backend \
    --region us-central1 \
    --to-revisions=REVISION-NAME=100
```

## Support

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [GCP Support](https://cloud.google.com/support)

---

**Note**: Replace `linkdisplay-app` with your actual project ID throughout this guide. 