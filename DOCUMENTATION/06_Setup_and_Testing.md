# 06. Setup and Testing

> **Recruitment prototype.** Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional.

This document covers installation, configuration, environment variables, test cases and a manual test script.

---

## 1. Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11 or newer |
| Node.js and npm | A current LTS version |
| PostgreSQL | A database URL, for example a free Neon project. For quick local runs without a database URL, the backend can use a local SQLite file |
| Groq API key | Free key from the Groq console, for the live AI assistant. Without it, the labelled fallback is used |
| Git | To clone the repository |

## 2. Repository structure

```
.
├── backend/               FastAPI application, seed script and tests
├── frontend/              React application
├── DOCUMENTATION/         These documents and the diagrams
├── README.md
└── .env.example           (a backend/.env.example is also provided)
```

## 3. Environment variables

Create a `.env` file in `backend/` by copying `.env.example`, then fill in the values. **Never commit `.env`.** `.env.example` contains placeholders only.

### Backend

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Production: yes | PostgreSQL connection string (for Neon, with SSL enabled). If unset, a local SQLite file is used for development |
| `JWT_SECRET` | Yes | Long random string used to sign tokens |
| `GROQ_API_KEY` | For live AI | Groq API key |
| `GROQ_MODEL` | No | Defaults to `openai/gpt-oss-120b` |
| `FRONTEND_ORIGIN` | Yes (hosted) | URL of the front end, used for CORS. Defaults to `http://localhost:5173` for local work |
| `PORT` | Hosted | Port the web service listens on (set by most hosts) |

### Frontend

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the backend API, for example `http://localhost:8000/api` locally or the hosted API URL |

Generate a secret for `JWT_SECRET` with: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

## 4. Run locally

### 4.1 Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env
python -m app.seed          # loads fictional demo data (safe to run again)
uvicorn app.main:app --reload --port 8000
```
Check: open `http://localhost:8000/docs` for the interactive API documentation and `http://localhost:8000/api/health` for `{"status":"ok"}`.

### 4.2 Frontend
```bash
cd frontend
npm install
cp .env.example .env        # set VITE_API_URL
npm run dev
```
Open the address shown in the terminal (normally `http://localhost:5173`).

### 4.3 Demo accounts
Test accounts for the citizen, CMO admin and officers are created by the seed script and listed in the root `README.md`. They are fictional and use the `example.test` email domain.

## 5. Run the automated tests

```bash
cd backend
pytest -v
```
The tests use an in-memory database and a mocked AI client, so they need no network, no API key and no database URL.

Expected result for the current suite: **18 tests, all passing.**

## 6. Test cases

| # | Area | Test case | Expected result |
|---|---|---|---|
| 1 | Auth | Register with valid data, then log in; try a wrong password | Registration succeeds; login returns a token; the wrong password returns 401 |
| 2 | Auth | Register with an email that already exists | 409 conflict |
| 3 | Access | A citizen opens another citizen's grievance | 403 |
| 4 | Access | An officer opens a grievance of another department | 403 |
| 5 | Access | A citizen calls a CMO endpoint | 403 |
| 6 | Submission | Submit a grievance | 201, unique reference number, first history row |
| 7 | Workflow | Full path Submitted, Under Review, In Progress, Resolved | Each step succeeds and history count matches |
| 8 | Workflow | Make an invalid move (for example Submitted straight to Resolved) | 409 |
| 9 | Workflow | Reopen a grievance that is not Resolved | 409; reopening from Resolved works |
| 10 | Feedback | Give feedback before resolution, and twice after | 409 both times; the first valid feedback succeeds |
| 11 | Overdue | A grievance with a due date in the past and status not Resolved | Counted as overdue; not counted once Resolved |
| 12 | Escalation | CMO escalates a grievance | Flag set, status unchanged, history row written |
| 13 | Uploads | Upload a wrong file type and an over-limit file | 415 and 413; a valid file is stored |
| 14 | Privacy | Public tracker for a grievance that has internal remarks | Internal remarks and personal data are absent |
| 15 | Statistics | CMO statistics against seeded data | Totals match the database |
| 16 | AI | Analysis with the model mocked to return valid JSON | Suggestion returned with source `groq` |
| 17 | AI | Analysis with the model mocked to fail | Result returned with source `fallback` |
| 18 | AI | Model returns a category outside the allowed list | Output rejected and the fallback is used |

## 7. Manual end-to-end test

Run this on the local or hosted application with the demo accounts.

| Step | Action | Expected result |
|---|---|---|
| 1 | Open the Home page | Banner and footer disclaimer visible; statistics and departments load |
| 2 | Register a new citizen and log in | Redirected to the citizen dashboard |
| 3 | Open Submit Grievance, type a complaint, click "Get AI suggestion" | Suggestion appears with the source label (`AI suggestion`) |
| 4 | Attach a small image and submit | Reference number shown (`CMK-2026-...`) |
| 5 | Open Track Grievance without logging in and paste the number | Status, department and history are shown, no personal data |
| 6 | Log in as the CMO | Counts and charts show stored data |
| 7 | Open the new grievance | Attachment opens; AI summary with Accept and Override is shown |
| 8 | Review it, then forward it to a department and an officer | Status becomes In Progress; history shows each step |
| 9 | Add one internal and one public remark | Both are stored; only the public one appears to the citizen |
| 10 | Log in as the assigned officer | Only that department's grievances are listed |
| 11 | Add a progress remark and submit an action-taken report | Assignment state becomes Report Submitted |
| 12 | Log in as the CMO and accept the report | Status becomes Resolved |
| 13 | Log in as the citizen | Update and full history visible; feedback form shown |
| 14 | Submit feedback, or reopen with a reason | Feedback saved, or the status becomes Reopened |
| 15 | Refresh the browser on a deep link such as `/cmo` | The page loads correctly |

## 8. Deployment

| Part | Setup |
|---|---|
| Database | A managed PostgreSQL instance (for example Neon). Put its connection string in `DATABASE_URL` |
| Backend | A Python web service. Root directory `backend`. Build command `pip install -r requirements.txt`. Start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the environment variables above on the host |
| Frontend | A static site. Build command `npm install && npm run build`; publish directory is the build output (`dist`). Set `VITE_API_URL`. Add a rewrite of all paths to `index.html` so direct links such as `/cmo` work after a refresh |
| Seeding | Run `python -m app.seed` once against the production `DATABASE_URL` |
| CORS | Set `FRONTEND_ORIGIN` on the backend to the deployed front-end URL |

Free-tier web services can sleep when idle. The first request after a pause may take up to a minute, and the front end shows a "server is waking up" message while it waits. Free-tier databases can also pause briefly after idle time.

## 9. Security checks before publishing

- Search the repository for secrets: the prefix `gsk_`, `postgresql://` connection strings, and `JWT_SECRET=` with a real value. Nothing should be found outside `.env`.
- Confirm `.env` and any local database file are listed in `.gitignore` and are not tracked.
- Confirm `.env.example` contains placeholders only.
- Use a dedicated API key for the hosted demo and revoke it after the assessment.

## 10. Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| Backend does not start | Check `DATABASE_URL` and `JWT_SECRET` are set; check the Python version |
| CORS error in the browser | `FRONTEND_ORIGIN` does not match the front-end URL exactly (including `https://` and no trailing slash) |
| Login works locally but not when hosted | `VITE_API_URL` points to localhost; rebuild the front end with the hosted API URL |
| First load is very slow | The free-tier host was asleep; wait up to a minute and refresh |
| AI suggestion always says "Keyword fallback" | `GROQ_API_KEY` is missing or invalid, or the free-tier limit was reached |
| Upload rejected | File must be JPG, PNG or PDF and at most 2 MB |
| 404 on refresh of a front-end page | The static host needs the rewrite to `index.html` |
| No data shown | Run the seed script against the correct database |
