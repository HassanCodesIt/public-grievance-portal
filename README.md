# CM Kerala Public Grievance Redressal Portal (Janasevanam · ജനസേവനം)

> **⚠️ RECRUITMENT PROTOTYPE DISCLAIMER**  
> **This application is an engineering prototype developed exclusively for the WhiteMatrix Software Solutions Machine Test (AI Full Stack Engineer).**  
> **It is NOT affiliated with, authorized by, or endorsed by the Government of Kerala or the Chief Minister's Office (CMO). All citizen grievances, officer profiles, department contacts, and administrative actions are completely fictional.**

---

## 📌 Executive Summary
**Janasevanam** is a full-stack, AI-augmented public grievance redressal portal built for state-level administrative governance. It accelerates citizen issue resolution through Groq-powered AI triage (`openai/gpt-oss-120b`) while strictly preserving **human-in-the-loop decision-making**: AI assists with classification, urgency, and summarization, but human administrators retain full authoritative control over official determinations, assignments, and closures.

### Core Stack
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, React Router 7
- **Backend:** FastAPI (Python 3.10+), Pydantic v2, SQLAlchemy 2.0, PyJWT, bcrypt
- **Database:** Serverless PostgreSQL on Neon (free tier) / SQLite for fast local testing
- **AI Engine:** Groq Cloud API with `openai/gpt-oss-120b` foundation model + labelled keyword fallback
- **Attachment Storage:** Embedded in PostgreSQL (`bytea` / `LargeBinary`, <= 2 MB) with magic bytes validation

---

## 🔑 Demo Login Accounts (Fictional Test Data)

All demo accounts use password **`Demo@123`**:

| Role | Email Address | Password | Permissions & Scope |
|---|---|---|---|
| **CMO Admin** | `cmo.admin@example.test` | `Demo@123` | Statewide overview, AI review & override, assignment, escalation, ATR decisions, analytics |
| **Department Officer (PWD)** | `officer.pwd@example.test` | `Demo@123` | Public Works department queue, progress remarks, Action-Taken Report submission |
| **Department Officer (Health)** | `officer.health@example.test` | `Demo@123` | Health and Family Welfare queue, progress remarks, ATR submission |
| **Citizen** | `citizen.demo@example.test` | `Demo@123` | Grievance submission with AI triage, file upload, personal dashboard, rating & reopen |

*Convenience Quick Logins:* The login page also features 1-click preset buttons for instant role switching without manual typing (`admin@janasevanam.example.test`, `officer@janasevanam.example.test`, `citizen@janasevanam.example.test`).

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 20.18+ (with `npm` or `pnpm`)
- Git

### 2. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/cm-kerala-grievance-portal.git
cd cm-kerala-grievance-portal

# Setup environment file
cp .env.example .env
```

### 3. Backend Setup & Run
```bash
cd backend

# Install Python requirements
pip install -r requirements.txt

# Seed the database (10 departments, demo users, 26 fictional grievances)
python -m app.seed

# Start the FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```
- API Base: `http://localhost:8000`
- Swagger / OpenAPI Docs: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/api/health`

### 4. Frontend Setup & Run
```bash
# Open a second terminal window
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

### 5. Run Automated Test Suite (18 Tests)
```bash
cd backend
python -m pytest -v
```
All **18 automated tests** will pass in ~10 seconds against an isolated in-memory test database.

---

## 🏛️ System Architecture

```
cm-kerala-grievance-portal/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, rate limiting, error handlers
│   │   ├── config.py            # Pydantic settings & env loader
│   │   ├── db.py                # SQLAlchemy engine & session factory
│   │   ├── models.py            # 10 core relational tables
│   │   ├── schemas.py           # Pydantic v2 schemas & validators
│   │   ├── security.py          # Direct bcrypt hashing, JWT issuance, require_role
│   │   ├── seed.py              # 26 realistic fictional grievances seed script
│   │   ├── routers/             # auth, public, ai, grievances, status, cmo, officer
│   │   └── services/            # workflow, ai_assistant, duplicates, stats, uploads
│   ├── tests/
│   │   ├── conftest.py          # In-memory SQLite fixture with isolated session
│   │   └── test_all_18.py       # Full 18 test cases per Section 8.2
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/                    # React 19 + TypeScript + Vite + Tailwind CSS v4
│   ├── src/
│   │   ├── pages/               # AuthPages, CitizenPages, CmoPages, OfficerPages, PublicPages
│   │   ├── api.ts               # Resilient dual-mode API client (live backend + mock fallback)
│   │   ├── components.tsx       # Governmental UI shell, status badges, timelines, modals
│   │   ├── routes.tsx           # Role-based protected routes
│   │   └── main.tsx             # React DOM entrypoint
│   └── package.json
├── DOCUMENTATION/               # Complete engineering documentation suite (7 markdown files)
│   ├── 01_Project_Overview.md
│   ├── 02_System_Architecture.md
│   ├── 03_Database_Design.md
│   ├── 04_API_Documentation.md
│   ├── 05_AI_Integration.md
│   ├── 06_Setup_and_Testing.md
│   ├── 07_User_Guide.md
│   └── images/
│       ├── architecture_diagram.svg / .png
│       └── er_diagram.svg / .png
├── README.md
├── .env.example
└── .gitignore
```

---

## 🤖 AI Triage & Safety Architecture

The portal leverages Groq's high-speed inference engine with `openai/gpt-oss-120b`:
1. **Delimited Prompt-Injection Defense:** Citizen complaint text is wrapped in strict `<<<USER_GRIEVANCE>>>` delimiters, with system prompt instructing the model to treat content as untrusted raw data.
2. **Deterministic Fallback Engine:** If the Groq API key is missing or encounters a timeout/rate limit, the system seamlessly engages an internal regex pattern classifier (`keyword_fallback_classifier`), flagged with `source: "fallback"` and a visible UI badge (*"Keyword fallback, not AI"*).
3. **SHA-256 In-Memory Cache:** Avoids token waste by caching identical complaints by SHA-256 hash.
4. **Duplicate Candidate Detection:** Compares new complaints against active open grievances in the same district from the previous 60 days using `difflib.SequenceMatcher`.
5. **No Autonomous Authority:** AI suggestions are advisory only. Official status changes, department assignments, and resolutions require human administrative action.

---

## ⚙️ Mandatory 5-State Workflow Lifecycle

Enforced strictly in `backend/app/services/workflow.py` with `transition()`:

```
[Citizen Submit] 
       ↓
  (Submitted)
       ↓  CMO Review & Confirm Category/Priority (SLA Computed)
 (Under Review)
       ↓  CMO Forwards to Department & Officer
  (In Progress) ←──────────────┐
       │ (Progress Remarks)    │ CMO Returns ATR for Rework
       │ (Officer Submits ATR) │
       ↓                       │
  [CMO Accepts ATR] ───────────┘
       ↓
   (Resolved)
       ↓  Citizen Reopens with Reason
   (Reopened) ──→ (Under Review)
```

- **SLA Deadlines:** High Priority = 3 days, Medium = 7 days, Low = 14 days.
- **Overdue Flagging:** Grievances where `now > due_at` and status != `Resolved` are flagged as **Overdue** on the CMO dashboard.
- **Immutable Audit Trail:** Every transition, remark, and escalation logs a row in `grievance_history`.

---

## ☁️ Deployment Guide (Render + Neon)

### 1. Database (Neon Serverless PostgreSQL)
1. Create a free PostgreSQL project at [neon.tech](https://neon.tech) (choose Singapore region `ap-southeast-1`).
2. Copy the connection string into `DATABASE_URL` in Render.

### 2. Backend (Render Web Service)
1. **Root Directory:** `backend`
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:**
   - `DATABASE_URL`: Your Neon Postgres connection string
   - `JWT_SECRET`: A secure 32+ character string
   - `GROQ_API_KEY`: Your Groq API key
   - `GROQ_MODEL`: `openai/gpt-oss-120b`
   - `FRONTEND_ORIGIN`: Your frontend URL (or `*`)
   - `ENV`: `production`

### 3. Frontend (Render Static Site or Vercel)
1. **Root Directory:** `frontend`
2. **Build Command:** `npm install && npm run build`
3. **Publish Directory:** `dist`
4. **Environment Variable:** `VITE_API_URL=https://your-backend-api.onrender.com/api`
5. **SPA Rewrites:** Included via `vercel.json` (rewrites `/*` to `/index.html`).

> **Cold Start Note:** Free-tier services on Render suspend after 15 minutes of inactivity. Initial request can take ~45–60 seconds to spin up. A free pinger (e.g. cron-job.org) can be scheduled on `/api/health` every 10 minutes to maintain active status.

---

## 🛠️ Tools and Services Disclosure
In compliance with the assessment guidelines, the following tools and external services were utilized:
- **Anthropic Claude & Coding Agent:** Technical planning and code generation.
- **Groq Cloud:** Runtime LLM inference with `openai/gpt-oss-120b`.
- **Neon:** Free serverless PostgreSQL hosting.
- **FastAPI, SQLAlchemy, PyJWT, bcrypt:** Backend application framework and security.
- **React, Vite, Tailwind CSS v4, Lucide React:** Frontend user experience.

---

## 📚 Complete Documentation Sitemap
Detailed architectural specifications and guides are located in the `DOCUMENTATION/` directory:
- [01_Project_Overview.md](DOCUMENTATION/01_Project_Overview.md)
- [02_System_Architecture.md](DOCUMENTATION/02_System_Architecture.md)
- [03_Database_Design.md](DOCUMENTATION/03_Database_Design.md)
- [04_API_Documentation.md](DOCUMENTATION/04_API_Documentation.md)
- [05_AI_Integration.md](DOCUMENTATION/05_AI_Integration.md)
- [06_Setup_and_Testing.md](DOCUMENTATION/06_Setup_and_Testing.md)
- [07_User_Guide.md](DOCUMENTATION/07_User_Guide.md)
- [System Architecture Diagram](DOCUMENTATION/images/architecture_diagram.png)
- [Database ER Diagram](DOCUMENTATION/images/er_diagram.png)
