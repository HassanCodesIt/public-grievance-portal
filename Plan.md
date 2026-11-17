# plan.md — CM Kerala Public Grievance Redressal Portal (Recruitment Prototype)

**Assessment:** WhiteMatrix Software Solutions, Machine Test, AI Full Stack Engineer
**Deadline:** 18 November 2026, 11:00 PM IST (late submissions may not be considered)
**Stack (your choice):** FastAPI backend, **React** frontend, free tools only, Groq `openai/gpt-oss-120b` for the LLM
**Working rule:** a working end-to-end grievance workflow beats any optional feature.

---

## 0. Read this first

### 0.1 Time plan
- Today is 17 Nov. You have, at most, about a day and a half. **Target: submit by 8:00 PM IST on 18 Nov**, which leaves 3 hours for deployment surprises.
- Deploy a skeleton at the end of Part 1 (not at the end). Most last-minute failures are hosting problems.
- Day 1 (17 Nov): Parts 1 and 2. Day 2 morning: Part 3. Day 2 afternoon: Part 4 and submit.

### 0.2 What you must submit
| Item | Requirement |
|---|---|
| Hosted link | **Mandatory.** Evaluators must open it without running anything locally |
| GitHub repo | Complete source code, meaningful structure |
| DOCUMENTATION folder | 7 markdown files (section 12) plus an architecture diagram and an ER diagram |
| Root files | `README.md` and `.env.example` (no real secrets) |
| Demo video | 3–5 minute screen recording of the main workflows |
| Demo logins | Test accounts in the README or the submission message |

### 0.3 Rules from the brief (check each at the end)
- [ ] Disclose AI tools and third-party services used (README section "Tools and services").
- [ ] Never commit credentials or secrets.
- [ ] Fictional data only. No real citizen grievances, no official government credentials.
- [ ] Label it clearly as a **recruitment prototype** on every page footer, the home banner and the README. Do not imply endorsement by the Government of Kerala or the Chief Minister's Office.
- [ ] No copied projects. You will be asked to explain your implementation in the technical interview, so read and understand every file the coding agent writes.
- [ ] AI suggestions must be reviewable by a human and must never make official decisions.
- [ ] A keyword classifier alone does not count as AI. Use the real Groq model, with a clearly **labelled** fallback.

---

## 1. Scoring map (100 marks) and where the effort goes

| Area | Marks | What earns it | Plan section |
|---|---|---|---|
| Frontend and UI/UX | 10 | Clean, responsive, consistent public site and dashboards | 7 |
| Backend and business logic | 20 | Workflow state machine, role rules, overdue and escalation logic | 3, 6 |
| Database design | 10 | Required entities, relations, constraints, indexes | 5 |
| API development | 15 | REST endpoints, validation, consistent errors | 6 |
| AI implementation | 15 | Real LLM, structured output, review step, safeguards, fallback | 4 |
| Workflow functionality | 15 | The full lifecycle works end to end with history | 3 |
| Documentation | 10 | 7 files, diagrams, README | 12 |
| Security and testing | 5 | Auth, RBAC, validation, tests | 8 |

Backend, workflow and AI are 50 marks. Protect their time.

---

## 2. Technology decisions

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 18+ with Vite, React Router, Recharts for charts, plain CSS (or Tailwind if setup is quick) | Meets "React or equivalent"; Recharts gives charts fast |
| Backend | FastAPI (Python), Pydantic v2, SQLAlchemy 2.0 | Your chosen stack; auto-generated API docs at `/docs` help the API marks |
| Database | **PostgreSQL on Neon (free)** | The brief wants a relational or document database. Render's free web service has an ephemeral filesystem, so SQLite files would be lost on restart. Neon keeps the data |
| Auth | JWT bearer tokens, role claim (`citizen`, `cmo_admin`, `officer`), bcrypt password hashing | Simple role-based access |
| AI | Groq API, `openai/gpt-oss-120b`, via the OpenAI-compatible SDK | Your chosen model, free tier |
| File storage | Attachments stored **inside Postgres** (`bytea`), max 2 MB, jpg/png/pdf | Free hosts lose local files; this avoids a fourth service |
| Hosting | Render (web service for the API, static site for React) plus Neon | All free, no credit card needed to start |
| Tests | pytest with FastAPI TestClient | Fast to write |

**Notes**
- Hash passwords with the `bcrypt` package directly or `argon2-cffi`. The older `passlib` can break with newer `bcrypt` versions.
- Keep the models portable (string statuses, `LargeBinary`) so tests can run on an in-memory SQLite database while production uses Postgres.
- Use `pool_pre_ping=True` and `sslmode=require` for Neon, because the database suspends when idle and the first query can be slow.

---

## 3. Roles and the mandatory workflow

### 3.1 Roles
| Role | Can do |
|---|---|
| Citizen | Register, log in, submit grievances, track, see own dashboard, give feedback, reopen |
| CMO admin | See everything, review, set final category and priority, assign to department/officer, remark, escalate, accept or return action reports, view statistics |
| Department officer | See only grievances assigned to their department, update progress, add remarks, submit an action-taken report |

### 3.2 Statuses (exactly these five)
`Submitted`, `Under Review`, `In Progress`, `Resolved`, `Reopened`

### 3.3 Transition rules (one function, `transition()`, enforces all of this)
| From | Action | To | Who | What gets recorded |
|---|---|---|---|---|
| none | Submit grievance | Submitted | Citizen | Reference ID, AI analysis, history row |
| Submitted | CMO reviews and confirms or overrides AI suggestions | Under Review | CMO | Final category, priority, history row |
| Under Review | CMO forwards to department and officer | In Progress | CMO | Assignment row (state: Assigned), history row |
| In Progress | Officer adds progress or investigation remark | In Progress | Officer | History row with remark |
| In Progress | Officer submits action-taken report | In Progress | Officer | Report saved, assignment state: Report Submitted, history row |
| In Progress | CMO accepts report | Resolved | CMO | Assignment state: Closed, history row, citizen sees the update |
| In Progress | CMO returns report for rework | In Progress | CMO | Assignment state: Returned, remark, history row |
| Resolved | Citizen reopens with a reason | Reopened | Citizen | History row with reason |
| Reopened | CMO reviews again | Under Review | CMO | History row |
| Any open status | CMO escalates | unchanged | CMO | Escalated flag, history row |

Invalid transitions return HTTP 409 with a clear message. **Every** status change writes a `grievance_history` row with the timestamp, the responsible user, the old status, the new status and the remark.

### 3.4 Remarks visibility
Each remark is `public` (citizen can see it) or `internal` (CMO and officers only). The citizen dashboard and the public tracker show public remarks only.

### 3.5 Overdue and escalation
- Fictional SLA by priority: High 3 days, Medium 7 days, Low 14 days. Store `due_at` and recompute when the CMO sets the final priority.
- Overdue = `now > due_at` and status is not `Resolved`. Compute it in queries and show it in the CMO counts.
- "Escalate" sets `escalated = true`, adds an internal remark and a history row.

### 3.6 Reference ID
`CMK-2026-000123`: created on the server after the grievance row is flushed, from the year plus the zero-padded primary key. Add a unique constraint.

---

## 4. AI Grievance Assistant (15 marks, design carefully)

### 4.1 What it does
When a citizen types a complaint, the backend calls Groq and returns:
| Field | Notes |
|---|---|
| `category` | One of the allowed categories |
| `department` | One of the department names in the database |
| `priority` | `Low`, `Medium` or `High` |
| `summary` | 1–2 sentences for the CMO |
| `confidence` | 0–1 |
| `reasoning` | One short sentence |
| `duplicate_candidates` | Optional: IDs of similar open grievances |
| `source` | `groq` or `fallback` |

### 4.2 Flow
1. Citizen types the description and clicks **Get AI suggestion** (`POST /api/ai/analyze`).
2. The form shows the suggestion with the label "AI suggestion, you can change it". The citizen accepts or edits the category.
3. On submit, the **server runs the analysis again** (never trust the client's copy) and stores it in `ai_analyses`, next to the citizen's final choice.
4. The CMO sees the AI summary, suggested department and suggested priority with **Accept** or **Override** buttons. The final values are the human's. The AI never changes a status.

### 4.3 Prompt and safety design
- System prompt sets the role (grievance triage assistant, no official decisions), lists the allowed categories, departments and priority definitions, and demands a single JSON object.
- Put the complaint inside clear delimiters and tell the model to treat it as data, not instructions (prompt-injection defence).
- Low temperature, `reasoning_effort` low, a token cap, a timeout of about 15 seconds.
- Validate the output with Pydantic. Reject anything outside the allowed lists.
- Cap input length (for example 2,000 characters). Tell users not to enter real personal data.
- Handle complaints in English and Malayalam: ask for the summary in English. Test one Malayalam sample.
- Cache results in memory by a hash of the text to save tokens. Groq's free plan limits for this model were roughly 30 requests per minute and 1,000 per day when I checked; confirm on your console.

### 4.4 Fallback (must be labelled)
If Groq fails, times out or returns invalid JSON, use a keyword classifier and return `source: "fallback"`. The UI shows "Keyword fallback, not AI". Document this limitation in `05_AI_Integration.md`.

### 4.5 Optional duplicate flag
Compare the new text with open grievances in the same district and category from the last 60 days (Python `difflib` or trigram similarity). Return candidates as "possible duplicates for human review". Never merge automatically. Drop this first if time is short.

---

## 5. Data model

Required entities are covered. Use integer primary keys, created and updated timestamps, and foreign keys with indexes on the filter columns.

| Table | Key fields |
|---|---|
| `users` | id, name, email (unique), mobile, password_hash, role, department_id (officers only), is_active |
| `departments` | id, name, description, is_featured |
| `grievances` | id, reference_no (unique), citizen_id, district, category, subject, description, priority, status, due_at, escalated, department_id (current), ai_summary, created_at, updated_at |
| `grievance_history` | id, grievance_id, from_status, to_status, remark, visibility, actor_id, actor_role, created_at |
| `department_assignments` | id, grievance_id, department_id, officer_id, assigned_by, state (Assigned, Report Submitted, Returned, Closed), assigned_at |
| `attachments` | id, grievance_id, assignment_id (nullable), uploaded_by, kind (grievance, action_report), filename, content_type, size, data (bytea) |
| `action_reports` | id, assignment_id, text, submitted_by, submitted_at, cmo_decision, cmo_remark |
| `citizen_feedback` | id, grievance_id, rating (1–5), comment, created_at (one per grievance) |
| `contact_enquiries` | id, name, email, subject, message, created_at |
| `ai_analyses` | id, grievance_id (nullable until submit), input_hash, category, department, priority, summary, confidence, source, model, raw_json, final_category, final_priority, reviewed_by, created_at |

Relationships to draw in the ER diagram: users 1–N grievances, grievances 1–N history, grievances 1–N assignments, departments 1–N assignments and officers, grievances 1–N attachments, grievances 1–1 feedback, grievances 1–N ai_analyses.

---

## 6. API (meets all eight minimum operations)

All routes under `/api`. Errors use one JSON shape: `{ "detail": "...", "code": "..." }`.

| Group | Method and path | Purpose | Access |
|---|---|---|---|
| Auth | POST `/auth/register` | Register (name, email, mobile, password) | Public |
| | POST `/auth/login` | Returns token and role | Public |
| | GET `/auth/me` | Current user | Any logged in |
| Public | GET `/departments` | Department list | Public |
| | GET `/stats/public` | Sample statistics for the home page | Public |
| | GET `/meta` | Districts, categories, statuses | Public |
| | POST `/contact` | Save a contact enquiry | Public |
| | GET `/track/{reference_no}` | Status, department, public history | Public |
| AI | POST `/ai/analyze` | AI grievance analysis | Citizen |
| Citizen | POST `/grievances` | Submit (multipart: fields plus optional file) | Citizen |
| | GET `/grievances/mine` | Own list and counts | Citizen |
| | GET `/grievances/{id}` | Own grievance with public history | Citizen |
| | POST `/grievances/{id}/feedback` | Rating and comment after resolution | Citizen |
| | POST `/grievances/{id}/reopen` | Reopen with reason | Citizen |
| | GET `/attachments/{id}` | Download if authorised | Owner, CMO, assigned officer |
| Status | PATCH `/grievances/{id}/status` | Role-checked transition | CMO, officer |
| CMO | GET `/cmo/grievances` | Filters: district, category, priority, status, overdue; pagination | CMO |
| | GET `/cmo/grievances/{id}` | Full record, AI analysis, history, assignments, reports | CMO |
| | PATCH `/cmo/grievances/{id}/review` | Set final category and priority, move to Under Review | CMO |
| | POST `/cmo/grievances/{id}/assign` | Forward to department and officer | CMO |
| | POST `/cmo/grievances/{id}/remarks` | Internal or public remark | CMO |
| | POST `/cmo/grievances/{id}/escalate` | Escalate a delayed grievance | CMO |
| | POST `/cmo/reports/{assignment_id}/decision` | Accept (Resolved) or return | CMO |
| | GET `/cmo/stats` | Totals, pending, resolved, overdue, by district, by department, by status | CMO |
| Officer | GET `/officer/grievances` | Only the officer's department | Officer |
| | GET `/officer/grievances/{id}` | Details and attachments | Officer |
| | POST `/officer/grievances/{id}/progress` | Remark and progress | Officer |
| | POST `/officer/grievances/{id}/action-report` | Report text plus optional file | Officer |
| Ops | GET `/health` | For the "waking up" banner and uptime pings | Public |

---

## 7. Frontend (React)

### 7.1 Routes and pages
| Area | Route | Content |
|---|---|---|
| Public | `/` | Intro, big **Submit Grievance** and **Track Grievance** buttons, sample statistics, featured departments, footer |
| | `/about` | Purpose, vision, mission, objectives |
| | `/how-it-works` | The five-step flow (submit, CMO review, assignment, action, resolution) |
| | `/departments` | Cards with name and short description |
| | `/contact` | Form saved to the database |
| | `/faq` | Accordion of questions |
| | `/track` | Search by reference number |
| Auth | `/register`, `/login` | Forms with validation |
| Citizen | `/dashboard` | Counts (total, pending, resolved), list, detail drawer, feedback and reopen |
| | `/submit` | Form with AI suggestion panel and file upload |
| CMO | `/cmo` | Count cards (total, pending, resolved, overdue), charts, filters, table |
| | `/cmo/grievances/:id` | Details, attachments, AI review, assign, remarks, escalate, report review, history timeline |
| Officer | `/officer` | Assigned list |
| | `/officer/grievances/:id` | Details, progress update, action-taken report |

### 7.2 UI rules
- A visible banner and footer on every page: "Recruitment prototype. Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office."
- Responsive layout, loading and empty states, friendly error messages.
- "Server is waking up" message that appears while `/api/health` is slow (Render free services sleep).
- Status badges with consistent colours, a history timeline, and "AI suggestion" labels.
- Route guards by role; store the token in memory plus `localStorage`, and clear it on logout.
- Never use `dangerouslySetInnerHTML`.

---

## 8. Security and testing (5 marks, but also protects the demo)

### 8.1 Security checklist
- [ ] Password hashing, minimum length, no passwords in logs
- [ ] JWT secret from the environment, expiry about 60 minutes, role claim checked server-side
- [ ] `require_role()` dependency on every protected route
- [ ] Object-level checks: a citizen sees only their own grievances; an officer only their department's
- [ ] Pydantic validation on all inputs (lengths, enums, email, 10-digit Indian mobile)
- [ ] Upload checks: extension, content type, magic bytes, 2 MB limit
- [ ] CORS limited to the frontend origin
- [ ] Rate limits on login, contact and AI endpoints (simple in-memory limiter)
- [ ] Public tracker returns no personal data and no internal remarks
- [ ] No secrets in the repo; `.env` in `.gitignore`; `.env.example` has placeholders only

### 8.2 Tests to write (about 18)
1. Register and login success and failure
2. Duplicate email rejected
3. Citizen cannot open another citizen's grievance
4. Officer cannot see another department's grievance
5. Citizen cannot call CMO endpoints
6. Submit creates a unique reference ID and a history row
7. Full happy path: Submitted, Under Review, In Progress, Resolved, with history count
8. Invalid transition returns 409
9. Reopen only from Resolved
10. Feedback only after Resolved, only once
11. Overdue calculation
12. Escalation writes history
13. Upload rejects a wrong type and an oversized file
14. Public tracker hides internal remarks
15. CMO stats match the seeded data
16. AI analyze returns valid JSON (Groq mocked)
17. AI fallback is used and labelled when Groq fails
18. AI output outside the allowed lists is rejected

---

## 9. Folder structure

```
cm-kerala-grievance-portal/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py, db.py, models.py, schemas.py
│   │   ├── security.py          # hashing, JWT, require_role
│   │   ├── routers/             # auth, public, grievances, cmo, officer, ai
│   │   ├── services/            # workflow.py, ai_assistant.py, duplicates.py, stats.py, uploads.py
│   │   └── seed.py              # fictional demo data
│   ├── tests/
│   └── requirements.txt
├── frontend/                    # Vite + React
│   └── src/ (pages, components, api, auth)
├── DOCUMENTATION/
│   ├── 01_Project_Overview.md ... 07_User_Guide.md
│   └── images/ (architecture and ER diagrams)
├── README.md
├── .env.example
└── .gitignore
```

---

## 10. Build plan in 4 parts

Work in order. Do not start the next part until "Done when" is true.

### Part 1 — Foundation, database, auth, early deploy (about 4–5 hours)
- [ ] Create the repo structure, `.gitignore`, `.env.example`, virtual environment, `requirements.txt`.
- [ ] Create a free Neon project (pick the Singapore region, closest to India) and put `DATABASE_URL` in `.env`.
- [ ] `config.py`, `db.py`, all models from section 5.
- [ ] `security.py`: hashing, JWT, `require_role`.
- [ ] Auth endpoints, `/health`, `/meta`, `/departments`.
- [ ] `seed.py`: departments, demo users for the three roles, about 25 fictional grievances in different districts, statuses and priorities, with history rows.
- [ ] Vite React app with router, layout, banner, login page and a role-based redirect.
- [ ] **Deploy the skeleton:** API on Render, frontend on Render static site (or Vercel), Neon connected, login works on the hosted link.
- **Done when:** you can log in as each demo role on the hosted URL.

### Part 2 — Public site, citizen portal, AI assistant (about 6 hours)
- [ ] Public pages: Home, About, How It Works, Departments, Contact (saves to DB), FAQ, Track.
- [ ] Submit grievance form with district, category, subject, description and optional file.
- [ ] Reference ID generation and history row on submit.
- [ ] Public tracker (`/track/{ref}`) and citizen dashboard with counts and detail view.
- [ ] Attachment upload and authorised download.
- [ ] AI assistant: `ai_assistant.py` (Groq call, validation, cache, labelled fallback), `/ai/analyze`, suggestion panel on the form, `ai_analyses` storage.
- **Done when:** a citizen can register, get an AI suggestion, submit with a file, receive a reference ID and track it.

### Part 3 — CMO and officer workflows, dashboards (about 6 hours)
- [ ] `workflow.py` with `transition()` and the rules in section 3.3.
- [ ] CMO list with filters and pagination, detail page, AI review (accept or override), assign, remarks, escalate.
- [ ] Officer list (own department only), progress update, action-taken report with optional file.
- [ ] CMO decision on the report (accept to Resolved, or return).
- [ ] Citizen feedback after Resolved and reopen.
- [ ] `/cmo/stats` and Recharts charts: by district, by department, by status; count cards including overdue.
- [ ] Overdue logic and escalation.
- **Done when:** one grievance can travel the whole lifecycle across the three roles, with every step visible in the history timeline.

### Part 4 — Security, tests, documentation, deploy, submit (about 5 hours)
- [ ] Run through the security checklist (8.1) and write the 18 tests (8.2).
- [ ] Add rate limits, CORS lock-down, friendly error pages.
- [ ] Write the DOCUMENTATION folder and `README.md` (section 12). Export the two diagrams as images.
- [ ] Redeploy, run the final hosted-link check (section 11.4), and seed the production database.
- [ ] Record the 3–5 minute demo (suggested order: citizen registers and submits with AI suggestion, CMO reviews and assigns, officer updates and submits report, CMO accepts, citizen sees update and gives feedback, dashboards, API docs).
- [ ] Push to GitHub, make sure the repo contains no secrets, send the submission (section 14).
- **Done when:** section 14 is fully ticked before 8:00 PM IST on 18 Nov.

### Prompts for your coding agent
Give the agent this `plan.md` first, then one prompt per part:
- **Rules for every prompt:** "Follow plan.md. Build only this part. Do not add features not in the plan. Keep the models portable (string statuses, LargeBinary). When done, list the files you changed and how to test it."
- **Part 1:** "Build Part 1 of plan.md: repo structure, Neon-ready SQLAlchemy models, auth with roles, health, meta and departments endpoints, the seed script, and a minimal React shell with login and role-based redirect."
- **Part 2:** "Build Part 2: the six public pages plus Track, the submit form with upload, reference ID generation, the citizen dashboard, and the AI assistant exactly as in section 4, including the labelled fallback and caching."
- **Part 3:** "Build Part 3: the workflow transition function from section 3.3, the CMO and officer endpoints and pages, report decisions, feedback and reopen, stats and charts, overdue and escalation."
- **Part 4:** "Audit the app against sections 3 to 8 of plan.md as a table (Present, Partial, Missing, with file and function). Do not fix anything yet." Then fix the gaps, add the tests, and write the docs.

---

## 11. Deployment (all free)

### 11.1 What each free service does (and its catch)
| Service | Use | Catch to plan around |
|---|---|---|
| Neon (Postgres) | Database | Suspends when idle; the first query after a pause can be slow. Storage is limited to roughly 0.5–1 GB depending on the source, which is plenty for a prototype |
| Render web service | FastAPI | Spins down after 15 minutes without traffic and takes about a minute to wake. Filesystem is ephemeral, so no local files or SQLite |
| Render static site (or Vercel) | React build | Stays up, so evaluators always see the page immediately |

Do **not** use Render's own free Postgres for this: free databases there expire after 30 days.

### 11.2 Settings
- **API (Render web service):** root directory `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend (static site):** build `npm install && npm run build`, publish directory `dist`, environment variable `VITE_API_URL`, and a rewrite of `/*` to `/index.html` so React Router deep links work (on Vercel use a `vercel.json` rewrite).
- **Environment variables (API):** `DATABASE_URL`, `JWT_SECRET`, `GROQ_API_KEY`, `GROQ_MODEL=openai/gpt-oss-120b`, `FRONTEND_ORIGIN`, `ENV=production`. Never commit them.
- **Seed production once:** run `python -m app.seed` locally with the production `DATABASE_URL`.

### 11.3 Cold-start plan
- The frontend shows "Server is waking up, this can take up to a minute" while `/api/health` is slow.
- Put a free pinger (for example cron-job.org) on `/api/health` every 10 minutes from the day before submission until the evaluation window ends. Render grants 750 free instance hours a month per workspace, so check you have not used them up on other services.
- Write the cold-start note in the README and in the submission message.

### 11.4 Final hosted-link check (do it in an incognito window)
- [ ] Home page loads, banner visible
- [ ] Register a new citizen, log in, submit with a file, get a reference ID
- [ ] Track by reference ID without logging in
- [ ] Log in as CMO, forward it; as officer, update and submit a report; as CMO, accept it
- [ ] Charts show data
- [ ] AI suggestion shows `source: groq` (and the fallback label appears if you temporarily break the key)
- [ ] Refresh on a deep link such as `/cmo` works

---

## 12. Documentation (10 marks, start early, write as you build)

| File | Put in it |
|---|---|
| `01_Project_Overview.md` | Problem statement, objectives, scope, feature list, recruitment-prototype disclaimer |
| `02_System_Architecture.md` | Layers (React, FastAPI, Postgres, Groq), request flow, deployment diagram, architecture image |
| `03_Database_Design.md` | Every table, columns, relationships, ER diagram image |
| `04_API_Documentation.md` | Each endpoint: method, path, parameters, request and response example, errors (copy from `/docs`) |
| `05_AI_Integration.md` | Model and API, prompt design, workflow, safeguards, human review, labelled fallback, limitations |
| `06_Setup_and_Testing.md` | Install steps, environment variables, how to seed, how to run tests, the 18 test cases |
| `07_User_Guide.md` | Step-by-step for citizens, CMO admins and officers |
| `README.md` | Overview, hosted link, demo accounts (test only), quick start, tools and services disclosure, cold-start note |
| `.env.example` | Variable names with placeholders only |

**Diagrams:** write them as Mermaid in the markdown (GitHub renders it) and also export PNGs into `DOCUMENTATION/images/`, so they show everywhere.

**Tools and services disclosure (in README):** Claude (planning), your coding agent (code generation), Groq with `openai/gpt-oss-120b` (runtime AI), Neon, Render, React, FastAPI and the open-source libraries used.

---

## 13. Demo data

- **Districts (14):** Thiruvananthapuram, Kollam, Pathanamthitta, Alappuzha, Kottayam, Idukki, Ernakulam, Thrissur, Palakkad, Malappuram, Kozhikode, Wayanad, Kannur, Kasaragod.
- **Sample departments:** Public Works, Health and Family Welfare, General Education, Water Resources, Electricity, Local Self Government, Civil Supplies, Revenue, Transport, Social Justice.
- **Categories:** Roads and Infrastructure, Healthcare, Education, Water Supply, Electricity, Waste and Sanitation, Public Distribution, Land and Revenue, Transport, Other.
- **Demo logins (test only, fictional, use the reserved `example.test` domain):**

| Role | Email | Password |
|---|---|---|
| CMO admin | `cmo.admin@example.test` | choose a demo password |
| Officer (Public Works) | `officer.pwd@example.test` | choose a demo password |
| Officer (Health) | `officer.health@example.test` | choose a demo password |
| Citizen | `citizen.demo@example.test` | choose a demo password |

Seed about 25 grievances across districts, categories, priorities and every status, including a few overdue ones, so the dashboards and charts are not empty. All names and complaints must be fictional.

---

## 14. Final submission checklist

- [ ] Hosted link works in incognito (section 11.4)
- [ ] GitHub repo is public (or accessible) and contains no secrets: search for your Groq key prefix `gsk_`, check `.env` is not in the file list
- [ ] `README.md`, `.env.example`, DOCUMENTATION folder (7 files) and both diagrams are in the repo
- [ ] Demo logins are in the README and the submission message
- [ ] Tools and services disclosure is in the README
- [ ] Recruitment-prototype disclaimer is on every page and in the README
- [ ] Demo video (3–5 minutes) is recorded and its link works
- [ ] Submission message includes: hosted link, GitHub link, video link, demo credentials, a note about the first-load delay on the free host
- [ ] Sent before **8:00 PM IST, 18 November 2026** (the deadline is 11:00 PM)

---

## 15. Cut lines and risks

**If you run short on time, drop in this order:**
1. Duplicate detection
2. Rate limiting
3. Visual polish and animations
4. Admin view for contact enquiries
5. Malayalam testing
6. Extra charts (keep at least district-wise and department-wise)

**Never drop:** the full workflow with history, role-based access, the real Groq AI with review and a labelled fallback, the hosted link, and the documentation folder.

| Risk | Mitigation |
|---|---|
| Hosting fails late | Deploy the skeleton in Part 1 and redeploy often |
| Render cold start looks like a broken site | Waking-up banner, pinger, note in README and submission message |
| Groq rate limit or outage | Caching, low token use, labelled fallback |
| Neon pause or slow first query | `pool_pre_ping`, retry once, warm with the health pinger |
| Uploaded files lost | Stored in Postgres, not on disk |
| Agent writes code you do not understand | Read each part after it is built; you must explain it in the interview |
| Secrets leak | `.gitignore`, `.env.example`, a final search before pushing |