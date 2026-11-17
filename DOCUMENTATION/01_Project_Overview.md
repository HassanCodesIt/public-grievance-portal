# 01. Project Overview — CM Kerala Public Grievance Redressal Portal

> **Recruitment Prototype Notice**  
> This application is an engineering prototype submitted for the **WhiteMatrix Software Solutions Machine Test (AI Full Stack Engineer)**.  
> It is strictly a fictional demonstration and is **not affiliated with, endorsed by, or operated by the Government of Kerala or the Chief Minister's Office (CMO)**. All citizen grievances, officer names, and government credentials are entirely fictional.

---

## 1. Problem Statement
Public grievance redressal systems face distinct operational bottlenecks:
1. **Misrouting & Triage Overload:** Thousands of citizen complaints arrive daily across diverse departments (Public Works, Water Resources, Health, KSEB, Revenue, etc.). Misclassified complaints waste valuable days being bounced across departments.
2. **Lack of Human-Centric Transparency:** Citizens often submit complaints into an administrative black box, with ambiguous progress statuses and no clear audit trail of who touched their file.
3. **Unchecked Automation Risks:** Naive AI implementations that automatically close, reject, or assign grievances create administrative hazards and public distrust.

## 2. Solution & Objectives
The **Janasevanam (ജനസേവനം)** Public Grievance Redressal Portal solves these challenges through:
- **AI-Assisted Triage with Human Governance:** Fast, structured grievance triage powered by Groq's high-throughput open LLM (`openai/gpt-oss-120b`), generating category suggestions, urgency priority, and concise executive summaries.
- **Strict Human-in-the-Loop Review:** AI suggestions **never** make official administrative decisions. CMO administrators inspect, confirm, or override AI recommendations before departmental assignment.
- **Auditable 5-State Workflow State Machine:** Strict lifecycle enforcement (`Submitted` → `Under Review` → `In Progress` → `Resolved` ⇄ `Reopened`) with mandatory immutable history logs (`grievance_history`).
- **Granular Role-Based Access Control (RBAC):** Distinct interfaces and object-level authorization for **Citizens**, **CMO Administrators**, and **Department Officers**.
- **Transparent Public Tracking:** Citizens can track public progress via unique Reference Numbers (`CMK-YYYY-XXXXXX`) while safeguarding sensitive personal data and internal administrative remarks.

---

## 3. Core Feature Matrix

| Functional Module | Citizen | CMO Admin | Department Officer | Public Guest |
|---|:---:|:---:|:---:|:---:|
| Register & Authenticate (JWT) | ✅ | ✅ | ✅ | — |
| AI Grievance Classification | ✅ (Preview) | ✅ (Review & Confirm) | — | — |
| Grievance Submission & File Upload | ✅ | — | — | — |
| Anonymous Public Reference Tracker | ✅ | ✅ | ✅ | ✅ |
| Role-Filtered Dashboards | ✅ (Own) | ✅ (All + SLA Overdue) | ✅ (Dept Only) | — |
| Workflow State Transitions | Reopen | Review, Assign, Escalate, ATR Decision | Progress Remarks, Submit ATR | — |
| Action-Taken Report (ATR) Workflow | Inspect (Public) | Accept / Return for Rework | Draft & Submit | — |
| Post-Resolution Citizen Feedback | ✅ (1–5 Stars) | Review Feedback | Review Feedback | — |
| Escalation & SLA Overdue Flags | — | ✅ | View Flag | — |
| Analytics & Visualization Charts | — | ✅ | — | ✅ (Public Stats) |

---

## 4. Scope and Guardrails
- **Fictional Data Only:** Test data uses the reserved `.example.test` domain and mock phone numbers.
- **Dual-Mode AI Resilience:** If the Groq API key is omitted, exhausted, or experiences network interruptions, the system automatically engages an in-memory heuristic keyword fallback engine clearly labeled in the user interface.
- **Attachment Storage:** Attachments (PNG, JPEG, PDF up to 2 MB) are verified via magic bytes and persisted securely in the database (`bytea` / `LargeBinary`) to avoid data loss on ephemeral hosting tiers.
