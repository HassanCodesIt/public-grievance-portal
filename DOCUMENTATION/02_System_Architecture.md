# 02. System Architecture — CM Kerala Public Grievance Redressal Portal

## 1. High-Level Architectural Layers

```mermaid
graph TD
    subgraph ClientLayer ["Client Layer (React 19 + TypeScript)"]
        UI_Citizen["Citizen Portal (/submit, /dashboard, /track)"]
        UI_CMO["CMO Admin Dashboard (/cmo, /cmo/grievances/:id)"]
        UI_Officer["Officer Workspace (/officer, /officer/grievances/:id)"]
        UI_Public["Public Landing, FAQs & Stats (/, /departments, /contact)"]
    end

    subgraph SecurityGate ["Security & Middleware Gate"]
        CORS["CORS Policy Middleware"]
        RL["In-Memory Rate Limiter (IP-based)"]
        JWT_MW["JWT Bearer Authentication & RBAC (require_role)"]
        VAL["Pydantic v2 Schema & Magic-Byte File Validation"]
    end

    subgraph BackendAPI ["Application Layer (FastAPI Backend)"]
        RouterAuth["Auth Router (/api/auth)"]
        RouterPublic["Public Router (/api/departments, /api/track)"]
        RouterCitizen["Grievances Router (/api/grievances)"]
        RouterCMO["CMO Router (/api/cmo)"]
        RouterOfficer["Officer Router (/api/officer)"]
        RouterAI["AI Router (/api/ai/analyze)"]
        
        SM["Workflow State Machine (services/workflow.py)"]
        StatsEngine["Aggregation & SLA Overdue Engine (services/stats.py)"]
    end

    subgraph AIEngine ["AI & Triage Layer"]
        GroqLLM["Groq Cloud API (openai/gpt-oss-120b)"]
        Cache["In-Memory SHA-256 Cache"]
        Fallback["Rule-Based Keyword Fallback Classifier"]
        DupEngine["Duplicate Detection Engine (difflib)"]
    end

    subgraph DataStorage ["Data & Persistence Layer"]
        PG[(PostgreSQL on Neon / SQLite for Tests)]
        BLOB[("PostgreSQL bytea (Embedded Attachments <= 2MB)")]
    end

    ClientLayer --> SecurityGate
    SecurityGate --> BackendAPI
    BackendAPI --> SM
    BackendAPI --> StatsEngine
    RouterAI --> Cache
    Cache -->|Cache Miss| GroqLLM
    GroqLLM -->|On Failure/Timeout| Fallback
    RouterAI --> DupEngine
    BackendAPI --> PG
    BackendAPI --> BLOB
```

---

## 2. Component Breakdown

### 2.1 Frontend Client (React 19 + Vite + Tailwind CSS v4)
- **Framework:** React 19 with Vite 8 development server and Rolldown/Rollup optimized bundling.
- **Routing & State:** React Router 7 declarative routing with protected route guards by user role claim (`citizen`, `cmo_admin`, `officer`).
- **Resilient Dual-Mode API Client (`api.ts`):** Talks directly to FastAPI backend over JSON and multipart `FormData`. If the backend is starting up (cold start) or offline, automatically switches to an in-memory mock store so all views remain responsive.
- **Theme & UI:** Clean governmental design language with custom status badges (`status-submitted`, `status-under-review`, etc.), priority indicators, responsive modals, and accessible Lucide SVG iconography.

### 2.2 API & Gateway (FastAPI + Pydantic v2)
- **FastAPI Framework:** Asynchronous, self-documenting REST API with OpenAPI/Swagger interactive documentation at `/docs` and `/redoc`.
- **Validation:** Pydantic v2 data models enforcing string length boundaries, Kerala district enums, category constraints, 10-digit Indian phone numbers, and strict status enums.
- **Rate Limiting:** In-memory bucket rate limiter protecting login, public contact form, and AI triage endpoints from denial-of-service attempts.
- **Attachment Sanitization (`uploads.py`):** Multi-stage validation checking file size (<= 2MB), allowed extensions (`.jpg`, `.jpeg`, `.png`, `.pdf`), content-type headers, and binary magic bytes (`\xff\xd8\xff`, `\x89PNG`, `%PDF`).

### 2.3 Persistence Layer (SQLAlchemy 2.0 + PostgreSQL / SQLite)
- **Database Engine:** SQLAlchemy 2.0 ORM with declarative mapping and relationships.
- **Production Target:** Serverless PostgreSQL on Neon with `pool_pre_ping=True` and connection resilience against serverless auto-suspend.
- **Test Target:** Fully isolated in-memory SQLite database (`sqlite:///:memory:`) using `StaticPool` to ensure zero disk side-effects during rapid test runs.
- **Internal Binary Storage:** Uploaded citizen evidence and officer action reports are stored directly in PostgreSQL as `bytea` (`LargeBinary`), eliminating dependency on external S3 buckets.

### 2.4 AI Assistant Layer (Groq `openai/gpt-oss-120b`)
- **Model:** Open-weights foundation model `openai/gpt-oss-120b` hosted on Groq's high-speed LPU infrastructure.
- **Prompt Injection Defense:** Delimited input (`<<<USER_GRIEVANCE>>>`) instructed strictly as inert data to classify, not instructions to execute.
- **Deterministic Fallback:** Keyword heuristic classifier with clearly labeled `source: "fallback"` if Groq rate limits, times out, or fails.
- **Deduplication:** Text similarity matching against active grievances within the same district from the previous 60 days.

---

## 3. End-to-End Request Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Citizen
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant AI as Groq / Fallback AI
    participant DB as PostgreSQL Database
    actor CMO as CMO Administrator
    actor Officer as Department Officer

    Citizen->>FE: Enters grievance description & district
    Citizen->>FE: Clicks "Get AI Suggestion"
    FE->>API: POST /api/ai/analyze
    API->>AI: Triage complaint text inside delimiters
    AI-->>API: JSON {category, department, priority, summary}
    API-->>FE: Return AI suggestion (source: groq/fallback)
    FE-->>Citizen: Display suggestion with edit/accept options

    Citizen->>FE: Submits grievance (+ optional document)
    FE->>API: POST /api/grievances (multipart)
    API->>DB: Insert Grievance (status: Submitted)
    API->>DB: Generate reference CMK-YYYY-XXXXXX
    API->>DB: Store AiAnalysis & GrievanceHistory audit row
    API-->>FE: Return grievance with reference number

    CMO->>FE: Inspects pending list
    FE->>API: GET /api/cmo/grievances?status=Submitted
    API-->>FE: Return queue
    CMO->>FE: Confirms category & priority
    FE->>API: PATCH /api/cmo/grievances/:id/review
    API->>DB: Status -> Under Review, recalculate SLA due_at

    CMO->>FE: Forwards to Department & Officer
    FE->>API: POST /api/cmo/grievances/:id/assign
    API->>DB: Status -> In Progress, creates DepartmentAssignment

    Officer->>FE: Views department queue
    FE->>API: GET /api/officer/grievances
    Officer->>FE: Submits Action-Taken Report (ATR)
    FE->>API: POST /api/officer/grievances/:id/action-report
    API->>DB: Assignment state -> Report Submitted

    CMO->>FE: Reviews Officer ATR
    FE->>API: POST /api/cmo/reports/:id/decision {decision: "accept"}
    API->>DB: Status -> Resolved, Assignment -> Closed

    Citizen->>FE: Views resolved grievance & gives feedback
    FE->>API: POST /api/grievances/:id/feedback {rating: 5}
    API->>DB: Insert CitizenFeedback record
```

