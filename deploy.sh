#!/bin/bash
# Deploy Houston Financial Navigator to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"houston-financial-navigator"}
REGION=${REGION:-"us-central1"}
MAIN_SERVICE_NAME="houston-financial-navigator"
AI_SERVICE_NAME="houston-ai-service"

echo "🚀 Deploying Houston Financial Navigator to Google Cloud"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Authenticate and set project
echo "📋 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID
gcloud auth configure-docker

# Build and deploy AI service first
echo "🤖 Building AI chatbot microservice..."
cd ai-service
gcloud builds submit --tag gcr.io/$PROJECT_ID/$AI_SERVICE_NAME:latest .

echo "🌐 Deploying AI service to Cloud Run..."
gcloud run deploy $AI_SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$AI_SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --quiet

# Get AI service URL
AI_SERVICE_URL=$(gcloud run services describe $AI_SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "AI Service deployed at: $AI_SERVICE_URL"

cd ..

# Build and deploy main application
echo "🏗️ Building main application..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$MAIN_SERVICE_NAME:latest .

echo "🌐 Deploying main application to Cloud Run..."
gcloud run deploy $MAIN_SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$MAIN_SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,AI_SERVICE_URL=$AI_SERVICE_URL" \
    --quiet

# Get main service URL
MAIN_SERVICE_URL=$(gcloud run services describe $MAIN_SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "Main application: $MAIN_SERVICE_URL"
echo "AI service: $AI_SERVICE_URL"
echo ""
echo "Next steps:"
echo "1. Set up secrets for API keys: gcloud secrets create nessie-api-key --data-file=..."
echo "2. Set up secrets for Gemini API: gcloud secrets create gemini-api-key --data-file=..."
echo "3. Update frontend VITE_API_BASE to: $MAIN_SERVICE_URL"