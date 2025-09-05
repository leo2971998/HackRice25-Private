#!/bin/bash
# Setup Google Cloud Project for Houston Financial Navigator

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"houston-financial-navigator"}
REGION=${REGION:-"us-central1"}

echo "🏗️ Setting up Google Cloud Project: $PROJECT_ID"

# Create project (if it doesn't exist)
echo "📋 Creating/setting project..."
gcloud projects create $PROJECT_ID --name="Houston Financial Navigator" || true
gcloud config set project $PROJECT_ID

# Enable billing (requires manual setup)
echo "💳 Please ensure billing is enabled for project $PROJECT_ID"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "Press Enter once billing is enabled..."

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Initialize Firestore
echo "🗄️ Initializing Firestore..."
gcloud firestore databases create --region=$REGION --type=firestore-native || true

# Create secrets (placeholder)
echo "🔐 Creating secret placeholders..."
echo "placeholder" | gcloud secrets create nessie-api-key --data-file=- || true
echo "placeholder" | gcloud secrets create gemini-api-key --data-file=- || true
echo "placeholder" | gcloud secrets create flask-secret --data-file=- || true

echo "✅ Google Cloud setup complete!"
echo ""
echo "Next steps:"
echo "1. Update secrets with real values:"
echo "   gcloud secrets versions add nessie-api-key --data-file=<(echo 'YOUR_NESSIE_KEY')"
echo "   gcloud secrets versions add gemini-api-key --data-file=<(echo 'YOUR_GEMINI_KEY')"
echo "   gcloud secrets versions add flask-secret --data-file=<(echo 'YOUR_FLASK_SECRET')"
echo ""
echo "2. Test Firestore connection:"
echo "   python test_google_cloud.py"
echo ""
echo "3. Deploy services:"
echo "   ./deploy.sh"