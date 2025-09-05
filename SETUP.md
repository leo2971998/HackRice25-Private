# Houston Financial Navigator - Setup Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Required - Capital One Nessie API
NESSIE_API_KEY=your_nessie_api_key_here
NESSIE_BASE=https://api.nessieisreal.com

# Required - Flask Security
FLASK_SECRET=your_super_secret_flask_key_here

# Required - Google Cloud Services
GOOGLE_CLOUD_PROJECT=houston-financial-navigator
GEMINI_API_KEY=your_gemini_api_key_here

# AI Service Configuration (for microservice architecture)
AI_SERVICE_URL=http://localhost:8080  # Local dev, or https://your-ai-service.run.app

# Optional - Google Services (for future Sheets integration)
GOOGLE_API_KEY=your_google_api_key_here
SHEET_ID=your_google_sheet_id_here

# Optional - Development
USE_MOCK=1                              # Set to 1 for offline demo mode
VITE_API_BASE=http://localhost:8000     # Frontend API base URL
```

## 🏗️ Google Cloud Project Implementation

### ✅ Phase 1: Google Cloud Foundation
- **Firestore Database Integration**: Complete database utility with connection testing
- **Gemini AI Integration**: AI-powered financial assistance chat with fallback to mock responses
- **Environment Configuration**: Updated environment variables for Google Cloud services
- **Google Cloud Dependencies**: Added `google-cloud-firestore` and `google-generativeai` packages

### ✅ Phase 2: Microservice Architecture
- **Main Application**: Dockerized Flask app with Cloud Run configuration
- **AI Chatbot Service**: Separate microservice for AI processing
- **Container Infrastructure**: Docker configurations for both services
- **Cloud Run Deployment**: YAML configurations and deployment scripts

### ✅ Phase 3: Integration & Demo Flow
- **Service Communication**: Main app can call AI microservice or fallback to local processing
- **Intelligent Routing**: Automatic fallback when AI service is unavailable
- **Demo Compatibility**: All existing demo functionality preserved

### ✅ Phase 4: Production Ready
- **Deployment Scripts**: Automated Google Cloud deployment with `./deploy.sh`
- **Setup Scripts**: Google Cloud project initialization with `./setup-gcloud.sh`
- **Security**: Secrets management and non-root container users
- **Monitoring**: Health checks and proper logging

## Phase 1 Completed Features

### ✅ Backend Enhancements
- **Idempotent Demo Seed**: `/demo/seed` endpoint prevents duplicate demo users
- **Mock Mode**: `USE_MOCK=1` enables offline operation with cached JSON
- **120s Caching**: GET requests cached for instant chart loading
- **Frozen Seed Data**: Consistent 1 deposit + 6 purchases for every demo

### ✅ Frontend Improvements
- **Modern Landing Page**: Professional gradient design with clear value propositions
- **Enhanced Navigation**: Updated navbar with all routes and proper branding
- **Improved Dashboard**: Added Income vs Expenses, Spending by Category, Balance Line (30d)
- **Demo Flow**: Landing → Start Demo → Demo Dashboard with live data

### ✅ Key Endpoints

#### Demo Endpoints
- `POST /demo/seed` - Create/reuse idempotent demo user
- `GET /demo/summary` - Get demo summary with mock fallback

#### User Endpoints  
- `POST /me/seed` - Enhanced with USE_MOCK support
- `GET /me/summary` - Enhanced with better mock data and caching

## Running the Application

### Local Development with AI Microservice

#### Option 1: Full Microservice Stack (Recommended for Google Cloud testing)
```bash
# Terminal 1: Start AI Chatbot Service
cd ai-service
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8080

# Terminal 2: Start Main Application  
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8000

# Terminal 3: Start Frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

#### Option 2: Single Application (Simpler for development)
```bash
# Set AI_SERVICE_URL to empty or remove from .env
# This will use local AI processing instead of microservice

# Terminal 1: Start Main Application
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8000

# Terminal 2: Start Frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### Testing Google Cloud Integration
```bash
# Test Firestore and Gemini AI connections
python test_google_cloud.py

# Expected output:
# ✅ Firestore connection (if credentials configured)
# ❌ Gemini API key not configured (falls back to mock)
# ✅ AI response generation working
```

### Full Demo Experience
1. Start services using Option 1 or 2 above
2. Visit: http://localhost:5173
3. Click "Start Demo" button
4. Experience: Landing → Demo Seed → Dashboard with live charts
5. Test AI Chat: Ask about "rent assistance in Houston"

## 🚀 Google Cloud Deployment

### Prerequisites
- Google Cloud SDK installed (`gcloud` command available)
- Docker installed
- Google Cloud Project with billing enabled

### Quick Deployment
```bash
# 1. Setup Google Cloud Project (one-time)
./setup-gcloud.sh

# 2. Update secrets with real API keys
gcloud secrets versions add nessie-api-key --data-file=<(echo 'YOUR_NESSIE_KEY')
gcloud secrets versions add gemini-api-key --data-file=<(echo 'YOUR_GEMINI_KEY')
gcloud secrets versions add flask-secret --data-file=<(echo 'YOUR_FLASK_SECRET')

# 3. Deploy to Cloud Run
./deploy.sh

# 4. Update frontend configuration
# Set VITE_API_BASE to the main service URL from deployment output
```

### Manual Deployment Steps
```bash
# Set project and authenticate
gcloud config set project houston-financial-navigator
gcloud auth configure-docker

# Build and deploy AI service
cd ai-service
gcloud builds submit --tag gcr.io/houston-financial-navigator/houston-ai-service
gcloud run deploy houston-ai-service --image gcr.io/houston-financial-navigator/houston-ai-service --region us-central1

# Build and deploy main application  
cd ..
gcloud builds submit --tag gcr.io/houston-financial-navigator/houston-financial-navigator
gcloud run deploy houston-financial-navigator --image gcr.io/houston-financial-navigator/houston-financial-navigator --region us-central1
```

## Production Deployment

### Environment Checklist
- [ ] `NESSIE_API_KEY` - Valid Capital One Nessie API key
- [ ] `NESSIE_BASE` - Nessie API base URL  
- [ ] `FLASK_SECRET` - Strong secret key for JWT signing
- [ ] `GEMINI_API_KEY` - Valid Google Gemini API key
- [ ] `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID
- [ ] `AI_SERVICE_URL` - URL of deployed AI microservice (for main app)

### Architecture Overview
```
Frontend (React/Vite) → Main App (Flask/Cloud Run) → AI Service (Flask/Cloud Run)
                                    ↓
                               Firestore Database
                                    ↓  
                              Gemini AI API
```

### Offline Fallback Plan
The application has multiple fallback layers:
1. **AI Service Unavailable**: Main app falls back to local AI processing
2. **Gemini API Unavailable**: Local AI falls back to mock responses  
3. **Nessie API Unavailable**: Set `USE_MOCK=1` for cached JSON fixtures
4. **Firestore Unavailable**: Application continues with local storage

## 90-Second Demo Script

1. **Landing (15s)**: "Houston Financial Navigator helps residents find aid and understand spending. I'll start a demo."
2. **Dashboard (45s)**: "Here's my balance, income vs expenses, spending by category, and recent activity from Capital One's Nessie sandbox."
3. **Export (10s)**: Click Export → "Data exported to Google Sheets."
4. **Chat (15s)**: Ask "rent assistance near 77002" → show source cards
5. **Close (5s)**: "We combine grounded AI with friendly finance dashboard. One-click onboarding, instant value."