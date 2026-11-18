# 04. API Documentation

> **Recruitment prototype.** Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional. Example values below are illustrative.

Interactive documentation (Swagger UI) is generated automatically by FastAPI at `/docs`, and ReDoc at `/redoc`, on the running backend.

---

## 1. Conventions

| Item | Detail |
|---|---|
| Base path | `/api` |
| Format | JSON, with camelCase field names. File uploads use `multipart/form-data` |
| Authentication | `Authorization: Bearer <accessToken>` (JWT from login) |
| Roles | `citizen`, `cmo_admin`, `officer`. "Public" means no token is needed |
| Dates | ISO 8601 timestamps in UTC |
| Pagination | Query parameters `page` (from 1) and `pageSize`; responses return `items`, `total`, `page`, `pageSize` |
| Statuses | `Submitted`, `Under Review`, `In Progress`, `Resolved`, `Reopened` |
| Priorities | `Low`, `Medium`, `High` |
| Reference number | `CMK-2026-000123` |

### 1.1 Error format

Every error uses the same shape:

```json
{ "detail": "Grievance not found", "code": "not_found" }
```

| HTTP status | Meaning |
|---|---|
| 400 | Bad request |
| 401 | Missing, invalid or expired token |
| 403 | Role or ownership check failed |
| 404 | Record not found |
| 409 | Conflict, for example an invalid status transition or duplicate email |
| 413 | Uploaded file too large (over 2 MB) |
| 415 | File type not allowed (only JPG, PNG, PDF) |
| 422 | Validation error (field details in `detail`) |
| 429 | Too many requests (rate limit) |
| 500 | Unexpected server error |

## 2. Endpoint summary

| Group | Method and path | Purpose | Access |
|---|---|---|---|
| Auth | POST `/auth/register` | Register a citizen | Public |
| | POST `/auth/login` | Log in, receive a token | Public |
| | GET `/auth/me` | Current user | Logged in |
| Public | GET `/health` | Health check | Public |
| | GET `/meta` | Districts, categories, statuses, priorities | Public |
| | GET `/departments` | Department list | Public |
| | GET `/stats/public` | Sample statistics for the home page | Public |
| | POST `/contact` | Save a contact enquiry | Public |
| | GET `/track/{referenceNo}` | Track a grievance | Public |
| AI | POST `/ai/analyze` | AI grievance analysis | Citizen |
| Citizen | POST `/grievances` | Submit a grievance | Citizen |
| | GET `/grievances/mine` | List own grievances with counts | Citizen |
| | GET `/grievances/{id}` | Own grievance detail | Citizen |
| | POST `/grievances/{id}/feedback` | Feedback after resolution | Citizen |
| | POST `/grievances/{id}/reopen` | Reopen a resolved grievance | Citizen |
| | GET `/attachments/{id}` | Download an attachment | Owner, CMO, assigned officer |
| Status | PATCH `/grievances/{id}/status` | Role-checked status update | CMO, officer |
| CMO | GET `/cmo/grievances` | List with filters | CMO |
| | GET `/cmo/grievances/{id}` | Full record | CMO |
| | PATCH `/cmo/grievances/{id}/review` | Set final category and priority | CMO |
| | POST `/cmo/grievances/{id}/assign` | Forward to department and officer | CMO |
| | POST `/cmo/grievances/{id}/remarks` | Add a remark | CMO |
| | POST `/cmo/grievances/{id}/escalate` | Escalate a grievance | CMO |
| | POST `/cmo/reports/{assignmentId}/decision` | Accept or return an action report | CMO |
| | GET `/cmo/stats` | Dashboard statistics | CMO |
| Officer | GET `/officer/grievances` | Own department's grievances | Officer |
| | GET `/officer/grievances/{id}` | Grievance detail | Officer |
| | POST `/officer/grievances/{id}/progress` | Add a progress remark | Officer |
| | POST `/officer/grievances/{id}/action-report` | Submit an action-taken report | Officer |

### Minimum operations required by the brief

| Required operation | Endpoint |
|---|---|
| Citizen registration and login | POST `/auth/register`, POST `/auth/login` |
| Submit grievance | POST `/grievances` |
| Retrieve and list grievances | GET `/grievances/mine`, GET `/cmo/grievances`, GET `/officer/grievances` |
| Track a grievance by ID | GET `/track/{referenceNo}` |
| Update grievance status | PATCH `/grievances/{id}/status` |
| Retrieve departments | GET `/departments` |
| Retrieve CMO statistics | GET `/cmo/stats` |
| AI grievance analysis | POST `/ai/analyze` |

---

## 3. Authentication

### POST `/api/auth/register`
Create a citizen account. Public.

Request:
```json
{
  "name": "Asha Nair",
  "email": "asha.demo@example.test",
  "mobile": "9876543210",
  "password": "ChooseAStrongPassword1"
}
```
Response `201`:
```json
{ "id": 12, "name": "Asha Nair", "email": "asha.demo@example.test", "role": "citizen" }
```
Errors: `409` email already registered; `422` invalid email, mobile number or short password.

### POST `/api/auth/login`
Request:
```json
{ "email": "asha.demo@example.test", "password": "ChooseAStrongPassword1" }
```
Response `200`:
```json
{
  "accessToken": "<jwt>",
  "tokenType": "bearer",
  "user": { "id": 12, "name": "Asha Nair", "role": "citizen" }
}
```
Errors: `401` wrong email or password. Logout is performed by the front end discarding the token.

### GET `/api/auth/me`
Returns the logged-in user (`id`, `name`, `email`, `role`, `departmentId` for officers).

---

## 4. Public endpoints

### GET `/api/health`
```json
{ "status": "ok" }
```

### GET `/api/meta`
```json
{
  "districts": ["Thiruvananthapuram", "Kollam", "..."],
  "categories": ["Roads and Infrastructure", "Healthcare", "Education", "..."],
  "statuses": ["Submitted", "Under Review", "In Progress", "Resolved", "Reopened"],
  "priorities": ["Low", "Medium", "High"]
}
```

### GET `/api/departments`
```json
[
  { "id": 1, "name": "Public Works", "description": "Roads, bridges and public buildings", "isFeatured": true }
]
```

### GET `/api/stats/public`
Sample statistics for the Home page, computed from stored data.
```json
{ "totalReceived": 25, "resolved": 6, "inProgress": 9, "averageDaysToResolve": 5.2 }
```

### POST `/api/contact`
Request:
```json
{ "name": "Ravi K", "email": "ravi.demo@example.test", "subject": "Question", "message": "How long does a review take?" }
```
Response `201`: `{ "id": 4, "message": "Enquiry received" }`. The enquiry is stored in `contact_enquiries`.

### GET `/api/track/{referenceNo}`
Public. Returns limited information only: no personal data and no internal remarks.

Response `200`:
```json
{
  "referenceNo": "CMK-2026-000123",
  "status": "In Progress",
  "department": "Public Works",
  "submittedAt": "2026-11-10T08:30:00Z",
  "history": [
    { "timestamp": "2026-11-10T08:30:00Z", "fromStatus": null, "toStatus": "Submitted", "remark": "Grievance submitted", "actorRole": "citizen" },
    { "timestamp": "2026-11-11T05:10:00Z", "fromStatus": "Submitted", "toStatus": "Under Review", "remark": "Reviewed by CMO", "actorRole": "cmo_admin" }
  ]
}
```
Errors: `404` reference not found.

---

## 5. AI analysis

### POST `/api/ai/analyze`
Role: citizen. Analyses a complaint and returns a suggestion. The result is a suggestion only and can be changed by the citizen before submitting and by the CMO later.

Request:
```json
{ "description": "The road near the market junction has large potholes and two bikes have fallen this week.", "district": "Palakkad" }
```
Response `200`:
```json
{
  "category": "Roads and Infrastructure",
  "department": "Public Works",
  "priority": "High",
  "summary": "Large potholes near the market junction are causing accidents and need urgent repair.",
  "confidence": 0.87,
  "reasoning": "Describes road damage that is causing injuries.",
  "duplicateCandidates": [],
  "source": "groq"
}
```
`source` is `groq` when the model answered, or `fallback` when the labelled keyword fallback was used. Limits: the description is capped at 2000 characters.

Errors: `422` empty or too long text; `429` rate limit.

---

## 6. Citizen endpoints

### POST `/api/grievances`
Role: citizen. Content type `multipart/form-data`.

| Field | Required | Notes |
|---|---|---|
| district | yes | One of the 14 districts |
| category | yes | One of the allowed categories |
| subject | yes | Short title |
| description | yes | Detailed complaint, up to 2000 characters |
| file | no | JPG, PNG or PDF, up to 2 MB |

Response `201`:
```json
{
  "id": 31,
  "referenceNo": "CMK-2026-000031",
  "status": "Submitted",
  "priority": "High",
  "dueAt": "2026-11-21T08:30:00Z",
  "createdAt": "2026-11-18T08:30:00Z"
}
```
The server generates the reference number, writes the first history row and stores a fresh AI analysis next to the citizen's final choice. Errors: `413`, `415`, `422`.

### GET `/api/grievances/mine`
Query: `page`, `pageSize`. Response:
```json
{
  "counts": { "total": 4, "pending": 3, "resolved": 1 },
  "items": [
    {
      "id": 31, "referenceNo": "CMK-2026-000031", "subject": "Damaged road near the market junction",
      "district": "Palakkad", "category": "Roads and Infrastructure", "priority": "High",
      "status": "Submitted", "department": null, "createdAt": "2026-11-18T08:30:00Z"
    }
  ],
  "total": 4, "page": 1, "pageSize": 10
}
```

### GET `/api/grievances/{id}`
Own grievance only (`403` otherwise). Returns the full grievance, attachments (id, filename), the current department, and the history with **public remarks only**.

### POST `/api/grievances/{id}/feedback`
Allowed only when the status is Resolved, and only once.
```json
{ "rating": 4, "comment": "Issue fixed, thank you." }
```
Response `201`. Errors: `409` not resolved or feedback already given; `422` rating outside 1 to 5.

### POST `/api/grievances/{id}/reopen`
Allowed only from Resolved.
```json
{ "reason": "The road is damaged again after one week." }
```
Response `200` with the new status `Reopened`. Errors: `409` not resolved; `422` missing reason.

### GET `/api/attachments/{id}`
Returns the file with its content type. Allowed for the owning citizen, the CMO, and the officer assigned to that grievance. Others receive `403`.

---

## 7. Status update

### PATCH `/api/grievances/{id}/status`
Role: CMO or officer. Uses the same workflow function as every other status change.
```json
{ "status": "In Progress", "remark": "Site inspection scheduled", "visibility": "public" }
```
Response `200`: updated grievance with the new `status` and the new history entry.
Errors: `403` role may not make this move or officer is not assigned; `409` invalid transition from the current status.

---

## 8. CMO endpoints

All require the `cmo_admin` role.

### GET `/api/cmo/grievances`
Query parameters (all optional): `district`, `category`, `priority`, `status`, `overdue` (true or false), `search` (reference number), `page`, `pageSize`.

Response:
```json
{
  "items": [
    {
      "id": 31, "referenceNo": "CMK-2026-000031", "subject": "Damaged road near the market junction",
      "district": "Palakkad", "category": "Roads and Infrastructure", "priority": "High", "status": "Submitted",
      "department": null, "dueAt": "2026-11-21T08:30:00Z", "overdue": false, "escalated": false
    }
  ],
  "total": 25, "page": 1, "pageSize": 10
}
```

### GET `/api/cmo/grievances/{id}`
Full record: complaint, citizen name, attachments, AI analysis (suggestion, source, final choices), the full history (public and internal remarks), assignments and action reports.

### PATCH `/api/cmo/grievances/{id}/review`
Confirms or overrides the AI suggestion and moves a Submitted or Reopened grievance to Under Review. Recalculates the due date from the final priority.
```json
{ "category": "Roads and Infrastructure", "priority": "High", "remark": "Confirmed AI suggestion" }
```

### POST `/api/cmo/grievances/{id}/assign`
Forwards the grievance and moves it to In Progress.
```json
{ "departmentId": 1, "officerId": 7, "remark": "Please inspect and report within 3 days" }
```
Response `200`. Errors: `409` not in Under Review; `422` officer does not belong to the department.

### POST `/api/cmo/grievances/{id}/remarks`
```json
{ "text": "Escalate if no response in 2 days", "visibility": "internal" }
```
`visibility` is `public` or `internal`. Internal remarks are never returned to citizens or the public tracker.

### POST `/api/cmo/grievances/{id}/escalate`
```json
{ "remark": "Overdue by 2 days, escalating to the department head" }
```
Sets the escalated flag, adds an internal remark and a history row. The status does not change.

### POST `/api/cmo/reports/{assignmentId}/decision`
```json
{ "decision": "accept", "remark": "Report verified" }
```
`decision` is `accept` (status becomes Resolved, assignment Closed) or `return` (status stays In Progress, assignment Returned; a remark is required).

### GET `/api/cmo/stats`
Statistics computed from stored data.
```json
{
  "total": 25, "pending": 14, "resolved": 6, "overdue": 3,
  "byDistrict": [ { "district": "Palakkad", "count": 4 } ],
  "byDepartment": [ { "department": "Public Works", "count": 7 } ],
  "byStatus": [ { "status": "In Progress", "count": 9 } ],
  "trend": [ { "date": "2026-11-17", "count": 3 } ]
}
```

---

## 9. Officer endpoints

All require the `officer` role and are limited to the officer's own department.

### GET `/api/officer/grievances`
Query: `page`, `pageSize`. Returns grievances forwarded to the officer's department with due date, overdue flag and assignment state (`Assigned`, `Report Submitted`, `Returned`, `Closed`).

### GET `/api/officer/grievances/{id}`
Complaint details, attachments, CMO instructions and remarks visible to officers, and the history. Another department's grievance returns `403`.

### POST `/api/officer/grievances/{id}/progress`
```json
{ "remark": "Inspection done. Repair material ordered.", "visibility": "public" }
```
The status stays In Progress and a history row is written.

### POST `/api/officer/grievances/{id}/action-report`
Content type `multipart/form-data`: `reportText` (required) and `file` (optional JPG, PNG or PDF up to 2 MB). Sets the assignment state to Report Submitted, ready for CMO review.

Response `201`: `{ "assignmentId": 15, "state": "Report Submitted" }`.

---

## 10. Rate limits

Login, contact and AI analysis endpoints are rate limited. Exceeding a limit returns `429` with the standard error body; the front end shows a friendly retry message.

## 11. Security summary for API consumers

- Always send the token as a Bearer header; tokens expire and must be refreshed by logging in again.
- A valid token is not enough: role and ownership are checked on every request.
- Never send real personal data; this is a prototype with fictional data.
