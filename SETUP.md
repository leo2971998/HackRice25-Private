# Houston Financial Navigator - Setup Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Required - Capital One Nessie API
NESSIE_API_KEY=your_nessie_api_key_here
NESSIE_BASE=https://api.nessieisreal.com

# Required - Flask Security
FLASK_SECRET=your_super_secret_flask_key_here

# Optional - Google Services (for future Sheets integration)
GOOGLE_API_KEY=your_google_api_key_here
SHEET_ID=your_google_sheet_id_here

# Optional - Development
USE_MOCK=1                              # Set to 1 for offline demo mode
VITE_API_BASE=http://localhost:8000     # Frontend API base URL
```

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

### Frontend Development
```bash
npm install
npm run dev
# Runs on http://localhost:5173
```

### Backend Development
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8000
```

### Full Demo Experience
1. Start frontend: `npm run dev`
2. Start backend: `python app.py` 
3. Visit: http://localhost:5173
4. Click "Start Demo" button
5. Experience: Landing → Demo Seed → Dashboard with live charts

## Production Deployment

### Environment Checklist
- [ ] `NESSIE_API_KEY` - Valid Capital One Nessie API key
- [ ] `NESSIE_BASE` - Nessie API base URL
- [ ] `FLASK_SECRET` - Strong secret key for JWT signing
- [ ] `GOOGLE_API_KEY` - For Sheets integration (optional)
- [ ] `SHEET_ID` - Target Google Sheet ID (optional)

### Offline Fallback Plan
Set `USE_MOCK=1` in production if Nessie API is unavailable:
- Demo will use cached JSON fixture
- Dashboard shows realistic spending categories
- Export feature shows "Demo mode" message

## 90-Second Demo Script

1. **Landing (15s)**: "Houston Financial Navigator helps residents find aid and understand spending. I'll start a demo."
2. **Dashboard (45s)**: "Here's my balance, income vs expenses, spending by category, and recent activity from Capital One's Nessie sandbox."
3. **Export (10s)**: Click Export → "Data exported to Google Sheets."
4. **Chat (15s)**: Ask "rent assistance near 77002" → show source cards
5. **Close (5s)**: "We combine grounded AI with friendly finance dashboard. One-click onboarding, instant value."