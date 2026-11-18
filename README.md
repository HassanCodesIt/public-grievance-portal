# Janasevanam (ജനസേവനം) — CM Kerala Public Grievance Redressal Portal

> **Recruitment prototype. Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional.**

---

## 📌 Overview

**Janasevanam (ജനസേവനം)** is an AI-augmented public grievance redressal prototype designed for state-level citizen service delivery. It streamlines citizen complaint submission, automated AI triage, department routing, action tracking, and resolution auditing while enforcing strict human-in-the-loop oversight.

---

## 🌐 Live Demo

| Component | URL |
|---|---|
| **Frontend Application** | `HOSTED_FRONTEND_URL` |
| **Backend API & Swagger Docs** | `HOSTED_API_URL` |

> [!NOTE]
> **Cold Start Notice:** The free-tier host spins down instances after a period of inactivity. The initial request or page load may take up to a minute to respond while containers warm up. If you encounter an initial delay or wake-up screen, please wait 30–60 seconds and refresh the page.

---

## 🔑 Demo Logins

All demo accounts use password: **`Demo@123`**  
*(These are fictional test accounts seeded exclusively for evaluation and testing.)*

| Role | Name | Email Address | Department / Scope | Password |
|---|---|---|---|---|
| **CMO Admin** | Ananya Menon | `cmo.admin@example.test` | Chief Minister's Office (Statewide) | `Demo@123` |
| **CMO Admin (Quick Login)** | Ananya Menon | `admin@janasevanam.example.test` | Chief Minister's Office (Preset) | `Demo@123` |
| **Department Officer** | Ravi Kumar | `officer.pwd@example.test` | Public Works | `Demo@123` |
| **Department Officer (Quick Login)** | Ravi Kumar | `officer@janasevanam.example.test` | Public Works (Preset) | `Demo@123` |
| **Department Officer** | Dr. Lakshmi Nair | `officer.health@example.test` | Health and Family Welfare | `Demo@123` |
| **Citizen** | Meera Krishnan | `citizen.demo@example.test` | Citizen Portal | `Demo@123` |
| **Citizen (Quick Login)** | Meera Krishnan | `citizen@janasevanam.example.test` | Citizen Portal (Preset) | `Demo@123` |
| **Citizen** | Arun Das | `arun.das@example.test` | Citizen Portal | `Demo@123` |
| **Citizen** | Nila Thomas | `nila.thomas@example.test` | Citizen Portal | `Demo@123` |
| **Citizen** | Devika Raj | `devika.raj@example.test` | Citizen Portal | `Demo@123` |
| **Citizen** | Fahad Ali | `fahad.ali@example.test` | Citizen Portal | `Demo@123` |

*(The login screen also provides 1-click quick-fill buttons for instant role switching without manual typing.)*

---

## 🛠️ Tools and Services

In accordance with disclosure requirements:
- **AI Coding Assistant:** Antigravity (Google DeepMind)
- **UI Design Tool:** Figma Make (used for baseline design token and layout export)
- **AI Assistant Model:** **Groq Cloud** with `openai/gpt-oss-120b` (sub-second LPU inference, structured JSON output, low temperature `0.1`, wrapped in strict prompt-injection delimiters, with deterministic regex keyword fallback)
- **Database Provider:** **Neon** (Serverless PostgreSQL with connection pooling)
- **Hosting Providers:** Vercel / Render
- **Frontend Framework & Libraries:** React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, React Router 7
- **Backend Framework & Libraries:** FastAPI (Python 3.10+), Pydantic v2, SQLAlchemy 2.0, PyJWT, bcrypt, python-jose, python-multipart, httpx, uvicorn
- **Testing Framework:** pytest 8.0, pytest-anyio

---

## ⚡ Quick-Start (Running Locally)

### 1. Backend Setup
```bash
cd backend

# Create virtual environment and activate
python -m venv venv
# On Windows PowerShell: .\venv\Scripts\Activate.ps1
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root or configure the following environment variable names (values should not be committed):
- `DATABASE_URL` (PostgreSQL connection string or `sqlite:///./grievances.db` for local test)
- `JWT_SECRET` (A strong random secret for signing authentication tokens)
- `GROQ_API_KEY` (API key from Groq Cloud; if omitted, deterministic fallback activates automatically)
- `GROQ_MODEL` (Defaults to `openai/gpt-oss-120b`)
- `FRONTEND_ORIGIN` (CORS origin, e.g., `http://localhost:5173` or `*`)
- `ENV` (`development` or `production`)

### 3. Database Seeding
Seed the 10 official government departments, demo users, and 26 realistic fictional grievances:
```bash
python -m app.seed
```

### 4. Running the Tests
Run the complete automated test suite (18 test cases verifying security, workflow, AI triage, rate limiting, and RBAC):
```bash
pytest backend/tests -v
```

### 5. Start Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Readiness Check: `http://localhost:8000/api/health`

### 6. Start Frontend
In a separate terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📚 Documentation

Comprehensive architectural design and engineering specifications are located in the [DOCUMENTATION](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION) folder:

- [01. Project Overview](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/01_Project_Overview.md) — Scope, goals, user personas, and assessment alignment.
- [02. System Architecture](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/02_System_Architecture.md) — Architectural patterns, request flow, and state machine diagrams.
- [03. Database Design](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/03_Database_Design.md) — 10-table relational schema, entity relationships, constraints, and audit trails.
- [04. API Documentation](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/04_API_Documentation.md) — Complete REST endpoint specifications, request/response formats, and error codes.
- [05. AI Integration](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/05_AI_Integration.md) — Groq `openai/gpt-oss-120b` triage, prompt-injection defense, duplicate detection, and human override safeguards.
- [06. Setup and Testing](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/06_Setup_and_Testing.md) — Step-by-step installation, test suite breakdown, and troubleshooting.
- [07. User Guide](file:///C:/Users/hassa/Downloads/CM%20PUBLIC%20GRIEVANCE%20READDRESSAL%20PORTAL/DOCUMENTATION/07_User_Guide.md) — End-to-end user manuals for Citizens, CMO Administrators, and Department Officers.
