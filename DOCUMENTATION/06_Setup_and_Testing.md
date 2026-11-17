# 06. Setup and Testing Guide — CM Kerala Public Grievance Redressal Portal

This guide provides step-by-step instructions for running the portal locally and executing the full automated test suite.

---

## 1. System Prerequisites
- **Python:** Version 3.10 or higher
- **Node.js:** Version 20.18 or higher (with `npm` or `pnpm`)
- **Git**

---

## 2. Environment Configuration
Copy the sample environment file to `.env`:
```bash
cp .env.example .env
```

Key environment variables:
| Variable | Description | Default / Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string (or SQLite fallback) | `sqlite:///./grievances.db` |
| `JWT_SECRET` | Secret key for JWT signing | `your-secure-random-secret-key-at-least-32-chars` |
| `GROQ_API_KEY` | Groq Cloud API Key | `gsk_...` (leave blank to test fallback) |
| `GROQ_MODEL` | Groq Model Name | `openai/gpt-oss-120b` |
| `FRONTEND_ORIGIN` | Allowed CORS origins | `http://localhost:5173,http://localhost:8443,*` |
| `ENV` | Environment identifier | `development` or `production` |

---

## 3. Backend Setup

### 3.1 Install Python Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 3.2 Seed Fictional Database
Seed the 10 official departments, demo login accounts, and 26 realistic fictional grievances:
```bash
cd backend
python -m app.seed
```

### 3.3 Run the FastAPI Development Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- API root: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

---

## 4. Frontend Setup

### 4.1 Install Dependencies
```bash
cd frontend
npm install
```

### 4.2 Start Frontend Development Server
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

### 4.3 Production Build Verification
Verify that TypeScript compilation and bundle packaging succeed:
```bash
cd frontend
npm run build
```

---

## 5. Automated Test Suite (18 Test Cases)

The backend includes a comprehensive pytest suite in `backend/tests/test_all_18.py` covering all 18 requirements from Section 8.2 of the project brief.

Tests run against an isolated in-memory SQLite database (`sqlite:///:memory:`) using `StaticPool` to ensure zero disk side-effects.

### Running the Tests
```bash
cd backend
python -m pytest -v
```

### Test Case Verification Matrix

| # | Test Function Name | Assertion & Verification |
|---|---|---|
| 1 | `test_01_register_and_login_success_and_failure` | Verifies account creation (`201`), JWT issuance on valid login (`200`), and rejected login on bad password (`401`). |
| 2 | `test_02_duplicate_email_rejected` | Asserts that registering a second user with the same email returns HTTP `400` with descriptive error. |
| 3 | `test_03_citizen_cannot_open_another_citizens_grievance` | Validates object-level security: Citizen B querying Citizen A's grievance is rejected with HTTP `403`. |
| 4 | `test_04_officer_cannot_see_another_departments_grievance` | Asserts that a PWD officer cannot access a Health and Family Welfare grievance (HTTP `403`). |
| 5 | `test_05_citizen_cannot_call_cmo_endpoints` | Confirms RBAC enforcement: citizens calling `/api/cmo/grievances` receive HTTP `403 Forbidden`. |
| 6 | `test_06_submit_creates_unique_reference_id_and_history_row` | Verifies grievance submission generates `CMK-YYYY-XXXXXX` and creates a `Submitted` history audit row. |
| 7 | `test_07_full_happy_path_workflow` | Tests complete lifecycle across roles: `Submitted` → `Under Review` (CMO) → `In Progress` (Assigned) → ATR filed (Officer) → `Resolved` (CMO), verifying history count >= 4. |
| 8 | `test_08_invalid_transition_returns_409` | Asserts state machine prevents jumping directly from `Submitted` to `Resolved` (returns HTTP `409 Conflict`). |
| 9 | `test_09_reopen_only_from_resolved` | Verifies that reopening from `In Progress` fails (`409`), while reopening from `Resolved` succeeds. |
| 10 | `test_10_feedback_only_after_resolved_only_once` | Confirms feedback before resolution is blocked (`400`), first feedback succeeds (`200`), and duplicate feedback is rejected (`400`). |
| 11 | `test_11_overdue_calculation` | Asserts that grievances with `due_at < now` are identified and returned by the `?overdue=true` query. |
| 12 | `test_12_escalation_writes_history` | Tests CMO escalation: sets `escalated = true` and creates an internal audit history row. |
| 13 | `test_13_upload_rejects_wrong_type_and_oversized_file` | Validates rejection of disallowed file extensions/magic bytes and files exceeding the 2 MB threshold (`400`). |
| 14 | `test_14_public_tracker_hides_internal_remarks` | Asserts public tracker `/api/track/{ref}` exposes public history while omitting `Internal` remarks. |
| 15 | `test_15_cmo_stats_calculation` | Verifies that `/api/cmo/stats` returns accurate counts for total, pending, resolved, overdue, and department distributions. |
| 16 | `test_16_ai_analyze_returns_valid_json_groq_mocked` | Mocks Groq API response and asserts structured triage JSON output (`source: groq`). |
| 17 | `test_17_ai_fallback_is_used_and_labelled_when_groq_fails` | Simulates Groq timeout/outage and asserts fallback keyword classifier takes over with `source: fallback`. |
| 18 | `test_18_ai_output_outside_allowed_lists_is_normalized` | Simulates LLM hallucinated categories/priorities and asserts backend normalizes to allowed enums. |
