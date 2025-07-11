#!/bin/bash

# LinkDisplay GCP Deployment Script
# This script deploys both backend and frontend to Google Cloud Platform

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # Replace with your GCP project ID
REGION="us-central1"
BACKEND_SERVICE="linkdisplay-backend"
FRONTEND_SERVICE="linkdisplay-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting LinkDisplay deployment to GCP...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  You are not authenticated with gcloud. Please run:${NC}"
    echo "gcloud auth login"
    exit 1
fi

# Set the project
echo -e "${YELLOW}📋 Setting GCP project to: ${PROJECT_ID}${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required GCP APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable appengine.googleapis.com

# Deploy Backend
echo -e "${GREEN}🔧 Deploying Backend...${NC}"
cd backend

# Build and deploy to Cloud Run
echo -e "${YELLOW}📦 Building backend Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE .

echo -e "${YELLOW}🚀 Deploying backend to Cloud Run...${NC}"
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production

# Get the backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format="value(status.url)")
echo -e "${GREEN}✅ Backend deployed at: ${BACKEND_URL}${NC}"

cd ..

# Deploy Frontend
echo -e "${GREEN}🔧 Deploying Frontend...${NC}"
cd frontend

# Update the API URL in the frontend
echo -e "${YELLOW}🔗 Updating API URL to: ${BACKEND_URL}${NC}"
sed -i.bak "s|http://localhost:3001|${BACKEND_URL}|g" src/App.js

# Build and deploy to Cloud Run
echo -e "${YELLOW}📦 Building frontend Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE .

echo -e "${YELLOW}🚀 Deploying frontend to Cloud Run...${NC}"
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 5

# Get the frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format="value(status.url)")
echo -e "${GREEN}✅ Frontend deployed at: ${FRONTEND_URL}${NC}"

# Restore the original API URL
mv src/App.js.bak src/App.js

cd ..

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📱 Frontend URL: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}🔧 Backend URL: ${BACKEND_URL}${NC}"
echo -e "${YELLOW}💡 To share publicly, append ?viewonly=true to the frontend URL${NC}"

# Optional: Set up custom domain
echo -e "${YELLOW}🌐 To set up a custom domain, run:${NC}"
echo "gcloud run domain-mappings create --service=$FRONTEND_SERVICE --domain=your-domain.com --region=$REGION" 