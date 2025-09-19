# Inflate-Wise – Project Guide

Inflate-Wise is an AI financial co-pilot that helps people understand and beat their **personal** inflation rate. Users connect their own credit cards or bank accounts through Plaid, Gemini categorises every transaction, and the backend maps spending to official Bureau of Labor Statistics (BLS) CPI categories to generate a personalised index. This guide documents the updated architecture and how to run the experience locally for hackathon demos.

---

## 1. Architecture at a glance

| Layer | Responsibilities | Key tech |
|-------|------------------|----------|
| **Frontend (Vite + React + Tailwind)** | Onboarding flow, Plaid sandbox simulation, inflation dashboard, Gemini assistant, receipt upload UI | `src/pages`, `src/components` |
| **Flask API** | Auth, Plaid token exchange, transaction sync, CPI weighting, Gemini receipts + assistant | `app.py`, `routes/`, `utils/` |
| **Firestore** | Stores users, Plaid metadata, category overrides, cached inflation snapshots | `utils/firestore_db.py`, `users` collection |
| **Gemini** | Transaction categorisation, personal coaching, receipt narratives | `utils/gemini.py` |
| **Plaid** | Secure account linking, balances, transactions | `utils/plaid_client.py` |

---

## 2. Environment configuration

Create a `.env` file in the project root:

```bash
# Flask session + frontend
FLASK_SECRET=change_me
VITE_API_BASE=http://localhost:8000

# Plaid (sandbox credentials recommended)
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox

# Gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=models/gemini-1.5-pro-latest

# Firestore
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
```

> **Note:** All integrations gracefully fall back to high-fidelity mock data when credentials are missing so you can demo without internet access.

---

## 3. Local development workflow

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
npm install

# 3. Run the backend
python app.py  # http://localhost:8000

# 4. In another terminal run the frontend
npm run dev    # http://localhost:5173
```

Plaid Link is simulated during hackathon demos. The onboarding page generates a link token and immediately calls the exchange endpoint with sandbox metadata so you can jump straight to the dashboard. Swap in the real Plaid Link flow post-hackathon by using the provided `link_token` in the Link JS widget and exchanging the returned `public_token` via `/plaid/exchange`.

---

## 4. Core flows

### 4.1 Account linking
1. `POST /plaid/link-token` creates a link token (returns mock data if credentials are missing).
2. `POST /plaid/exchange` stores the Plaid access token, item id, institution metadata, and resets the transaction cursor.
3. `GET /plaid/status` summarises balances and connection state for the onboarding UI.

### 4.2 Transactions + CPI mapping
1. `GET /transactions` pulls new transactions via Plaid `transactions/sync`.
2. `utils.gemini.categorize_transaction` maps descriptions to one of the app categories.
3. `utils.inflation.calculate_personal_inflation` converts categories to BLS series IDs and computes a weighted personal CPI.
4. User overrides are stored in Firestore (`set_category_override`) and immediately influence future calculations.

### 4.3 Gemini assistant
- `POST /assistant/ask` provides the user's latest inflation snapshot to Gemini before generating a response.
- The assistant can reference personal CPI, national CPI, top drivers, and spending weights directly in the answer.

### 4.4 Receipt ingestion
- `POST /uploads/receipt` accepts a list of line items + total and asks Gemini to summarise the impact. (Swap in the Gemini Vision API for true OCR when ready.)

---

## 5. Frontend highlights

- **Dashboard** – shows personal vs national CPI, category weights, override dropdowns, and receipt intelligence.
- **Onboarding** – demonstrates Plaid Link token generation and sandbox exchange for rapid demos.
- **Chat** – Gemini assistant grounded in personal data with ready-to-use prompts.
- **Inflation Lab** – narrative view explaining function calling, the CPI pipeline, and demo choreography.
- **Learn** – curated modules explaining personal inflation, CPI mapping, and how to pitch the project.

---

## 6. Demo script for judges

1. **Link an account** on the onboarding page (uses Plaid sandbox + mock fallback).
2. **Show the dashboard** to highlight the personal CPI calculation and top drivers.
3. **Override a category** to prove the CPI immediately updates.
4. **Upload a receipt** to trigger the Gemini narrative.
5. **Ask the assistant** why personal inflation is higher and receive a data-backed explanation.

---

## 7. Testing & diagnostics

| Command | Purpose |
|---------|---------|
| `python app.py` | Quick health check (`/healthz`) |
| `pytest` | Run Python tests (add new ones in `tests/` as functionality expands) |
| `npm run build` | Ensure the React app compiles |

Remember that the Plaid + Gemini integrations fall back to mock data, so automated tests can run without external credentials.

---

## 8. Next steps

- Replace the sandbox Plaid flow with production Link and persist transaction cursors per user.
- Upgrade receipt ingestion to use Gemini Vision images instead of typed line items.
- Extend Firestore caching to store historical CPI snapshots for trend charts.
- Deploy the Flask API and React frontend to Cloud Run + Firebase Hosting for real users.

Happy hacking, and good luck at HackRice!
