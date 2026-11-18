# 01. Project Overview

**Project:** Janasevanam (ജനസേവനം), a Public Grievance Redressal Portal
**Purpose:** Recruitment assessment prototype (WhiteMatrix Software Solutions, AI Full Stack Engineer machine test)

> **Recruitment prototype.** Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data in this project is fictional. No real citizen grievances are collected and no official credentials are used.

---

## 1. Problem statement

Citizens face problems with public infrastructure, healthcare, education and other public services. When there is no single, trackable channel to raise them, complaints get lost between offices, citizens cannot see what happened to them, and the Chief Minister's Office (CMO) cannot see which complaints are delayed or which departments are slow.

The assignment asks for a working prototype where citizens submit grievances, the CMO reviews them and forwards them to the right department, officers act on them, and every step stays visible and traceable until the grievance is resolved or reopened.

## 2. Objectives

1. Give citizens one place to submit a grievance, receive a unique reference number and follow its progress.
2. Give the CMO a central dashboard to review, prioritise, forward, monitor and escalate grievances.
3. Give department officers a focused inbox limited to their own department, with a way to report the action taken.
4. Record every status change with a timestamp and the responsible user, so each grievance is traceable for its whole life.
5. Use an AI assistant to speed up triage (category, department, priority, summary, possible duplicates) while keeping every decision with a human.
6. Provide statistics (counts, overdue, district-wise and department-wise views) built from stored data.

## 3. Users and roles

| Role | Who they are | Main abilities |
|---|---|---|
| Public visitor | Anyone | Read the public pages, track a grievance by reference number (limited information only) |
| Citizen | Registered user | Submit grievances with optional attachment, get AI suggestions, track, view own dashboard, give feedback, reopen |
| CMO admin | Administrator in the CMO | See all grievances, filter, review AI suggestions, set final category and priority, forward to a department and officer, add remarks, escalate, review action reports, view statistics |
| Department officer | Officer of one department | See only grievances forwarded to their department, add progress remarks, submit an action-taken report |

## 4. Scope

### In scope
- Public website: Home, About Us, How It Works, Departments, Contact Us, FAQ, Track Grievance
- Citizen portal: registration, login and logout, grievance submission, reference number, tracking, dashboard, feedback and reopening
- CMO dashboard and department officer dashboard
- Mandatory workflow with five statuses and a full history
- AI Grievance Assistant using the Groq API, with human review and a labelled fallback
- File upload and authorised retrieval of attachments
- Role-based access control, validation, automated tests
- Deployment as a hosted application

### Out of scope (by design)
- Real citizen data, real government credentials, official emblems or logos
- Integration with any real government system
- Email, SMS or push notifications (updates appear inside the application)
- Payments, mobile apps, multilingual interface translation
- Production-scale performance, high availability and formal security certification

## 5. Features

### 5.1 Public website
| Page | Content |
|---|---|
| Home | Introduction, navigation, prominent Submit Grievance and Track Grievance actions, sample statistics, featured departments, footer with the prototype disclaimer |
| About Us | Purpose, vision, mission and objectives |
| How It Works | Submission, CMO review, department assignment, action and resolution |
| Departments | Sample departments with names and short descriptions, loaded from the backend |
| Contact Us | Form with name, email, subject and message; each enquiry is saved in the database |
| FAQ | Questions about submitting and tracking grievances |
| Track Grievance | Search by reference number; shows status, assigned department and the public status history, never personal data or internal remarks |

### 5.2 Citizen portal
- Registration with name, email, mobile number and password; login and logout
- Submit a grievance with district, category, subject, detailed description and an optional image or document
- Unique reference number after submission, in the format `CMK-2026-000123`
- AI suggestion for category, department, priority and summary before submitting, which the citizen can accept or change
- Dashboard with submitted grievances, pending and resolved counts and details of earlier complaints
- Remarks from the CMO and officers (public ones only), feedback after resolution, and the option to reopen a resolved grievance with a reason

### 5.3 CMO dashboard
- All grievances with total, pending, resolved and overdue counts
- Filters by district, category, priority, status and overdue
- Grievance detail page with attachments, AI analysis, history, assignments and reports
- Accept or override the AI suggestion; set the final category and priority
- Forward to a department and officer; add public or internal remarks; escalate delayed grievances
- Review action-taken reports: accept (Resolved) or return for rework
- District-wise and department-wise statistics as charts, from stored data

### 5.4 Department officer dashboard
- Secure login with assigned credentials
- List limited to grievances forwarded to the officer's department
- Complaint details and attachments
- Progress remarks and an action-taken report (text and optional file) submitted back to the CMO

### 5.5 AI Grievance Assistant
- Analyses the complaint text and suggests a category, a department and a priority (Low, Medium or High)
- Writes a short summary for the CMO
- Optionally flags possible duplicate complaints for human review
- Always labelled as a suggestion; never makes an official decision
- Falls back to a clearly labelled keyword classifier if the model is unavailable

## 6. Grievance lifecycle

Statuses: **Submitted, Under Review, In Progress, Resolved, Reopened.**

1. A citizen submits a grievance (status **Submitted**). The system generates the reference number.
2. The CMO reviews it and confirms or changes the AI suggestions (**Under Review**).
3. The CMO forwards it to a department and officer (**In Progress**).
4. The officer investigates, adds remarks and submits an action-taken report.
5. The CMO reviews the report. Accepting it makes the grievance **Resolved**; returning it keeps it **In Progress** for rework.
6. The citizen sees the update and can give feedback, or reopen a resolved grievance (**Reopened**), which goes back to CMO review.

Every status change is stored with its timestamp, the responsible user and role, the old and new status and a remark. The full transition table is in `02_System_Architecture.md`.

## 7. Key design decisions

| Decision | Reason |
|---|---|
| AI only suggests; humans decide | The brief forbids AI from making official decisions |
| Citizen sees public remarks only | Internal CMO notes stay confidential |
| One transition function enforces all status changes | Guarantees valid transitions and a complete history |
| Attachments stored in the database | Free hosting platforms do not keep local files between restarts |
| Fictional service-level targets (High 3 days, Medium 7, Low 14) | Needed to calculate "overdue" in a prototype |
| Public tracker returns limited data | Protects citizen privacy |

## 8. Technology summary

| Layer | Technology |
|---|---|
| Frontend | React with Tailwind CSS |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL (Neon) |
| Authentication | JWT bearer tokens with role-based access |
| AI | Groq API, model `openai/gpt-oss-120b` |
| Testing | pytest |

Details: `02_System_Architecture.md`. The tools used to build the project (AI coding assistants, design tool and services) are disclosed in the root `README.md`.

## 9. Document map

| File | Content |
|---|---|
| `01_Project_Overview.md` | This document |
| `02_System_Architecture.md` | Architecture, flows, security, deployment |
| `03_Database_Design.md` | Schema, relationships, ER diagram |
| `04_API_Documentation.md` | Endpoints with examples |
| `05_AI_Integration.md` | AI design, safeguards, limitations |
| `06_Setup_and_Testing.md` | Installation, configuration, test cases |
| `07_User_Guide.md` | How each role uses the system |
