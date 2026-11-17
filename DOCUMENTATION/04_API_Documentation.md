# 04. API Documentation — CM Kerala Public Grievance Redressal Portal

Interactive OpenAPI/Swagger documentation is served at `/docs` and `/redoc` when the backend is running.

All responses use standard HTTP status codes. Errors adhere strictly to:
```json
{
  "detail": "Error description message",
  "code": "ERROR_CODE_STRING"
}
```

---

## 1. Authentication Endpoints (`/api/auth`)

### 1.1 `POST /api/auth/register`
Register a new citizen or officer account.
- **Access:** Public
- **Request Body (JSON):**
```json
{
  "name": "Meera Krishnan",
  "email": "citizen.demo@example.test",
  "mobile": "9847012345",
  "password": "Password@123",
  "role": "citizen"
}
```
- **Success Response (`201 Created`):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "Meera Krishnan",
    "email": "citizen.demo@example.test",
    "mobile": "9847012345",
    "role": "citizen",
    "department_id": null,
    "is_active": true,
    "created_at": "2026-11-17T14:30:00Z"
  }
}
```

### 1.2 `POST /api/auth/login`
Authenticate with email and password to receive a Bearer JWT.
- **Access:** Public
- **Request Body (JSON):**
```json
{
  "email": "cmo.admin@example.test",
  "password": "Demo@123"
}
```
- **Success Response (`200 OK`):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "Ananya Menon",
    "email": "cmo.admin@example.test",
    "role": "cmo_admin",
    "is_active": true
  }
}
```

### 1.3 `GET /api/auth/me`
Retrieve profile of currently authenticated user.
- **Access:** Any authenticated user (`Authorization: Bearer <token>`)
- **Success Response (`200 OK`):** User profile object.

---

## 2. Public Endpoints (`/api`)

### 2.1 `GET /api/departments`
Lists all 10 departments, their mandate descriptions, and featured flags.
- **Access:** Public
- **Success Response (`200 OK`):** Array of department objects.

### 2.2 `GET /api/stats/public`
Aggregated counter statistics for the landing page.
- **Access:** Public
- **Response (`200 OK`):**
```json
{
  "total": 1248,
  "resolved": 914,
  "inProgress": 246,
  "averageDays": 6.2
}
```

### 2.3 `GET /api/meta`
Metadata listing all 14 Kerala districts, 10 categories, and 5 statuses.
- **Access:** Public

### 2.4 `POST /api/contact`
Persists a public contact inquiry in the database.
- **Access:** Public
- **Request Body (JSON):** `{ "name": "...", "email": "...", "subject": "...", "message": "..." }`

### 2.5 `GET /api/track/{reference_no}`
Search public grievance progress by reference number (`CMK-YYYY-XXXXXX`).
- **Access:** Public
- **Security Rule:** Does not disclose private citizen contact info or internal administrative remarks.
- **Success Response (`200 OK`):**
```json
{
  "id": "1",
  "referenceNo": "CMK-2026-000001",
  "district": "Ernakulam",
  "category": "Roads and Infrastructure",
  "subject": "Damaged road near the market junction",
  "status": "In Progress",
  "priority": "High",
  "department": "Public Works",
  "history": [
    {
      "timestamp": "2026-11-10T10:00:00Z",
      "actorName": "Citizen",
      "actorRole": "Citizen",
      "toStatus": "Submitted",
      "remark": "Grievance submitted and reference number generated.",
      "visibility": "Public"
    }
  ]
}
```

---

## 3. AI Grievance Assistant (`/api/ai`)

### 3.1 `POST /api/ai/analyze`
Triage grievance description text with Groq LLM (`openai/gpt-oss-120b`) with prompt-injection defense and heuristic fallback.
- **Access:** Authenticated Citizen
- **Request Body (JSON):**
```json
{
  "description": "Severe flooding on Aluva market road due to collapsed storm drainage culvert.",
  "district": "Ernakulam"
}
```
- **Success Response (`200 OK`):**
```json
{
  "category": "Roads and Infrastructure",
  "department": "Public Works",
  "priority": "High",
  "summary": "Resident reports severe street flooding caused by a collapsed drainage culvert on Aluva market road.",
  "confidence": 0.92,
  "reasoning": "Identified critical civic infrastructure damage and flooding hazard.",
  "source": "groq",
  "model": "openai/gpt-oss-120b",
  "duplicate_candidates": []
}
```

---

## 4. Citizen Operations (`/api/grievances`)

### 4.1 `POST /api/grievances`
Submit a grievance with optional evidence upload (multipart form).
- **Access:** Citizen
- **Form Fields:** `district`, `category`, `subject`, `description`, `priority`, optional `file`
- **Success Response (`201 Created`):** Grievance detail object with generated `referenceNo`.

### 4.2 `GET /api/grievances/mine`
List all grievances submitted by the logged-in citizen.
- **Access:** Citizen

### 4.3 `GET /api/grievances/{id}`
Retrieve a single grievance record. Enforces object-level access (citizen can view only their own).
- **Access:** Grievance Owner, CMO, Assigned Officer

### 4.4 `POST /api/grievances/{id}/feedback`
Submit 1–5 star rating and comments. Permitted **only** when grievance status is `Resolved`, and only once per grievance.
- **Access:** Grievance Owner
- **Request Body:** `{ "rating": 5, "comment": "Issue fixed promptly." }`

### 4.5 `POST /api/grievances/{id}/reopen`
Reopen a previously resolved grievance with justification. Permitted **only** from `Resolved`.
- **Access:** Grievance Owner
- **Request Body:** `{ "reason": "Pothole reappeared after monsoon downpour." }`

### 4.6 `GET /api/attachments/{id}`
Download binary attachment. Authorized strictly for Owner, CMO, and assigned Officer.

---

## 5. CMO Administration (`/api/cmo`)

### 5.1 `GET /api/cmo/grievances`
List grievances with multi-parameter filtering (`status`, `district`, `category`, `priority`, `overdue`, `search`) and pagination (`page`, `limit`).
- **Access:** CMO Admin

### 5.2 `GET /api/cmo/grievances/{id}`
Inspect full administrative grievance record, including internal history, AI analyses audit rows, assignments, and ATRs.
- **Access:** CMO Admin

### 5.3 `PATCH /api/cmo/grievances/{id}/review`
CMO review confirming human choice of category and priority; moves status to `Under Review`.
- **Access:** CMO Admin
- **Request Body:** `{ "category": "Roads and Infrastructure", "priority": "High", "remark": "CMO confirmed priority." }`

### 5.4 `POST /api/cmo/grievances/{id}/assign`
Route grievance to department and nodal officer; moves status to `In Progress` and sets assignment state to `Assigned`.
- **Access:** CMO Admin
- **Request Body:** `{ "department_id": 1, "officer_id": 2, "remark": "Forwarded to PWD Division." }`

### 5.5 `POST /api/cmo/grievances/{id}/remarks`
Append administrative remark (Public or Internal) without altering workflow status.
- **Access:** CMO Admin
- **Request Body:** `{ "remark": "Inspection team contacted.", "visibility": "Internal" }`

### 5.6 `POST /api/cmo/grievances/{id}/escalate`
Mark grievance as `escalated = true` and log internal escalation entry.
- **Access:** CMO Admin

### 5.7 `POST /api/cmo/reports/{assignment_id}/decision`
Review Action-Taken Report: accept (transitions status to `Resolved`, assignment to `Closed`) or return for rework (status stays `In Progress`, assignment to `Returned`).
- **Access:** CMO Admin
- **Request Body:** `{ "decision": "accept", "remark": "Work confirmed complete." }`

### 5.8 `GET /api/cmo/stats`
Analytics payload: total counts, pending, resolved, SLA overdue, and breakdowns by district, department, and priority.
- **Access:** CMO Admin

---

## 6. Department Officer Operations (`/api/officer`)

### 6.1 `GET /api/officer/grievances`
List grievances assigned to the logged-in officer's department.
- **Access:** Department Officer

### 6.2 `GET /api/officer/grievances/{id}`
View grievance assigned to officer's department. Returns HTTP 403 if assigned to another department.
- **Access:** Department Officer

### 6.3 `POST /api/officer/grievances/{id}/progress`
Log progress notes or field inspection updates to grievance history.
- **Access:** Department Officer
- **Request Body:** `{ "remark": "Site inspection scheduled for 10:00 AM." }`

### 6.4 `POST /api/officer/grievances/{id}/action-report`
Submit final Action-Taken Report with optional evidence document. Sets assignment state to `Report Submitted`.
- **Access:** Department Officer
- **Form Fields:** `report` (text), optional `file`

---

## 7. Operations (`/api/health`)
### 7.1 `GET /api/health`
Health readiness probe.
- **Access:** Public
- **Response (`200 OK`):** `{ "status": "ok", "service": "...", "timestamp": "...", "env": "..." }`
