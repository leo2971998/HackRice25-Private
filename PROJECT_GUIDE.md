# Houston Financial Navigator – Unified Project Guide

This guide combines the setup notes, cloud integration details, AI agent docs, and admin instructions for the TrustAgent / Houston Financial Navigator project. Use it as the single source of truth for environment prep, data integrations, conversational AI, and deployment.

---

## 1. Platform Overview

| Layer | Responsibilities | Key Tech |
|-------|------------------|----------|
| **Frontend (Vite/React + Tailwind)** | Authenticated dashboards, TrustAgent chat with saved history, onboarding/demo flows | `src/pages`, `src/components`, Vite dev server |
| **Flask API** | Auth, Nessie demos, TrustAgent orchestration, AP2 automations, chat endpoints | `app.py`, `routes/`, `utils/` |
| **AI Microservice (optional)** | Offloads conversational reasoning when `AI_SERVICE_URL` is provided | `ai-service/app.py` |
| **Firestore** | Persists users, chat sessions, AP2 mandates, agent state | `utils/firestore_db.py`, `/chat_sessions` collection |
| **Google Cloud Integrations** | Gemini responses, Firestore, Cloud Run deployment tooling | `setup-gcloud.sh`, `deploy.sh`, `test_google_cloud.py` |
| **Capital One Nessie Sandbox** | Demo banking data used by dashboards & automations | `routes/me_nessie.py`, `routes/nessie_admin.py` |

The React chat experience now mirrors the Firebase prototype: conversations are stored in Firestore, surfaced in a sidebar, and streamed through `/ask` with Gemini-backed fallbacks when credentials are present.

---

## 2. Environment Configuration

Create a `.env` in the repository root:

```bash
# Authentication & session security
FLASK_SECRET=change_me_super_secret

# Nessie sandbox (required for demo seeding / admin sandbox)
NESSIE_API_KEY=your_nessie_api_key
NESSIE_BASE=https://api.nessieisreal.com

# Google Cloud services
GOOGLE_CLOUD_PROJECT=houston-financial-navigator
GEMINI_API_KEY=your_gemini_key # optional when relying on fallbacks

# Optional: external AI microservice
AI_SERVICE_URL=http://localhost:8080

# Frontend configuration
VITE_API_BASE=http://localhost:8000
VITE_FIREBASE_API_KEY=demo-or-real-api-key
VITE_FIREBASE_AUTH_DOMAIN=demo.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=gen-lang-client-0536110235
VITE_FIREBASE_STORAGE_BUCKET=demo.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef

# Local development helpers
USE_MOCK=1
```

Additional notes:

- Provide a service account JSON and point `GOOGLE_APPLICATION_CREDENTIALS` to it when running Firestore locally.
- The Firebase config powers the optional `ChatInterface` prototype and enables Firestore emulator support in dev.

---

## 3. Local Development Workflows

### Option A – Full Microservice Stack (mirrors Cloud Run deployment)

```bash
# Terminal 1 – AI microservice
cd ai-service
pip install -r requirements.txt
python app.py  # http://localhost:8080

# Terminal 2 – Flask API
pip install -r requirements.txt
python app.py  # http://localhost:8000

# Terminal 3 – React frontend
npm install
npm run dev    # http://localhost:5173
```

### Option B – Simplified Stack (local AI fallback)

Leave `AI_SERVICE_URL` empty or unset and run only the main Flask app plus the React client. The `/ask` endpoint will execute `process_financial_query` directly, using Gemini if credentials are present and falling back to semantic-search responses otherwise.

### Quick Diagnostics

```bash
# Validate Firestore + Gemini connectivity
python test_google_cloud.py

# Inspect Firestore portal endpoints
pytest test_portal.py

# Exercise AP2 automation scenarios
python test_phases_integration.py
```

---

## 4. Conversational AI & Firestore Persistence

### Backend Enhancements

`routes/chat.py` now exposes:

- `POST /chat/sessions` – create a persisted chat session for the authenticated user.
- `GET /chat/sessions` – list recent sessions, ordered by last update.
- `GET /chat/sessions/<session_id>` – fetch messages and metadata (timestamps, counts).
- `POST /ask` – handles questions, optionally creating/using a Firestore session when a user cookie is present.

Flow summary:

1. Client loads sessions with `/chat/sessions` and selects one to view message history.
2. `/ask` writes the user prompt + AI summary into `chat_sessions/{sessionId}.messages`, updating `message_count`, `last_message`, and auto-titling on the first question.
3. Stored history is passed to the AI agent (Gemini or fallback) to preserve context across turns.

### Frontend Experience

`src/pages/ChatPage.tsx` introduces a sidebar navigation similar to the Firebase prototype:

- Authenticated users see saved conversations with timestamps and message counts.
- “New” creates a session immediately and resets the chat window.
- Unauthenticated visitors still receive answers, but conversations remain transient with a login prompt in the sidebar.
- Messages and cited sources stream into the main pane, with quick prompts available through `QuickChips`.

### Firestore Collections

| Collection | Purpose | Relevant Utilities |
|------------|---------|--------------------|
| `users` | Profile data, Nessie linkage, trust metadata | `create_user`, `get_user`, … |
| `chat_sessions` | Messages array, context, message counters | `create_chat_session`, `add_message_to_session`, `get_user_chat_sessions` |
| `ap2_transactions` | Intent/cart/payment mandates | `create_ap2_transaction`, `update_ap2_transaction` |
| `agent_state` | Agent memory, pending actions | `create_agent_state`, `get_agent_state` |

Real-time listeners can be attached via `listen_to_chat_session` for dashboards or live updates if desired.

---

## 5. AI Agent Capabilities (Gemini + Fallback)

`utils/ai_agent.py` powers the assistant with:

- **Contextual prompts** – blends user profile, conversation history, and Houston program datasets.
- **Intent classification** – scores requests (urgent assistance, program search, application help, budgeting support).
- **Action plans** – returns summaries, next steps, follow-up questions, and resource citations.
- **Resilience** – gracefully degrades to TF-IDF answers and canned guidance when Gemini credentials are unavailable.

When `AI_SERVICE_URL` is defined, `/ask` forwards the prompt to the dedicated AI microservice (`ai-service/app.py`) for horizontal scaling; otherwise, it stays in-process.

---

## 6. Authentication & Admin Workflows

- Registration accepts a `role` (`user` or `admin`). Admins are redirected to `/admin` after login.
- `routes/auth.py` issues JWT cookies (`session`) and provides helpers: `require_auth`, `require_admin`.
- Admin dashboard (`/admin`) unlocks Nessie sandbox controls and Firestore portal tools.
- CLI helpers:
  ```bash
  curl -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"Pass123!","first_name":"Demo","last_name":"Admin","role":"admin"}'
  ```

Troubleshooting tips:

1. **“Email already registered”** – delete the row from `app.db` or use a new address.
2. **403 on `/admin`** – confirm the account’s `role` column is `admin` and the JWT cookie is present.
3. **Missing role data** – ensure `FLASK_SECRET` is stable between server restarts so cookies stay valid.

---

## 7. Financial Data Integrations

### Nessie Sandbox

- `/demo/seed` provisions a repeatable customer with deposits/purchases for dashboard charts.
- `/me/seed`, `/me/summary`, and admin Nessie endpoints rely on the `NESSIE_API_KEY` or fall back to rich mock data when `USE_MOCK=1`.

### AP2 Automation & TrustEngine

- `src/ap2_protocol.py` implements dataclasses for intent/cart/payment mandates with HMAC signatures and trust scoring.
- `routes/ap2.py` + `routes/smart_finance.py` expose mandate creation, savings plans, and scenario analysis.
- Firestore persistence ensures automations appear on the TrustAgent dashboard and survive restarts.

---

## 8. Google Cloud Tooling & Deployment

1. **Prerequisites** – Install the Google Cloud SDK and Docker. Enable billing on your project.
2. **Bootstrap** – `./setup-gcloud.sh` configures APIs, IAM bindings, and Artifact Registry repos.
3. **Secrets** – Store keys with Secret Manager (`nessie-api-key`, `gemini-api-key`, `flask-secret`).
4. **Deploy** – `./deploy.sh` builds both containers, pushes to Artifact Registry, and deploys Cloud Run services for the main API and AI microservice.
5. **Post-deploy** – update `VITE_API_BASE` to the Cloud Run URL and redeploy the frontend (e.g., Vercel, Firebase Hosting, or static host).

Run `python test_google_cloud.py` before pushing to confirm Firestore connectivity with the active service account.

---

## 9. Testing & Quality Gates

| Command | Purpose |
|---------|---------|
| `python test_google_cloud.py` | Verifies Firestore CRUD, Gemini access (with graceful fallbacks) |
| `pytest test_portal.py` | Ensures Firestore portal routes are wired correctly |
| `python test_phases_integration.py` | Validates AP2 protocol and automation scenarios |
| `npm run build` | Type-checks the React app and validates Tailwind usage |

(Per user instruction, skip `npm run lint` / ESLint in this workflow.)

---

## 10. Tips & Gotchas

- **Firestore Credentials** – Without a service account the app logs warnings and continues in mock mode; saved conversations require valid credentials.
- **Session Persistence** – `/ask` automatically creates a session when an authenticated user without an active thread sends a prompt.
- **Local Storage vs Firestore** – Unauthenticated visitors operate entirely in-memory; once they log in, the sidebar activates and conversations persist.
- **Fallback Resilience** – If the AI microservice or Gemini is unreachable, the assistant still returns actionable Houston-specific advice using embedded datasets.
- **Cleanup Utilities** – `utils/firestore_db.cleanup_expired_data()` removes chat sessions older than seven days; hook it into cron or Cloud Scheduler for production.

---

By consolidating every operational detail into this guide, you can provision infrastructure, build locally, manage conversations with Firestore, and deploy the Houston Financial Navigator with minimal guesswork.
