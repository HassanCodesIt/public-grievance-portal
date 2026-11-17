# 07. User Guide — CM Kerala Public Grievance Redressal Portal

This guide provides step-by-step walkthroughs for each of the three user roles in the recruitment prototype.

---

## 1. Demo Credentials (Test Only)

All accounts use fictional credentials ending in `.example.test` with password `Demo@123`:

| Role | Email Address | Password | Department / Scope |
|---|---|---|---|
| **CMO Admin** | `cmo.admin@example.test` | `Demo@123` | Statewide Administration, All Departments |
| **Department Officer (PWD)** | `officer.pwd@example.test` | `Demo@123` | Public Works Department |
| **Department Officer (Health)** | `officer.health@example.test` | `Demo@123` | Health and Family Welfare |
| **Citizen** | `citizen.demo@example.test` | `Demo@123` | Public Submissions & Tracking |

*Tip: The login screen also features 1-click role presets for immediate testing.*

---

## 2. Citizen Walkthrough

### Step 1: Submit a Grievance with AI Triage
1. Navigate to `/login` and sign in as `citizen.demo@example.test` (or register a new account at `/register`).
2. Click **Submit Grievance** in the navigation bar.
3. Select your **District** (e.g. *Ernakulam*) and begin typing your description:
   > *"Severe water leak from main distribution pipeline near Aluva junction. Water is gushing onto the road and flooding nearby shops."*
4. Click **Get AI suggestion**:
   - The Groq AI model (`openai/gpt-oss-120b`) analyzes your text in sub-second time.
   - The card shows suggested category (*Water Supply*), suggested department (*Water Resources*), and urgency priority (*High*).
   - If Groq is unreachable, the system automatically uses the labelled keyword fallback.
5. Review the suggestion. You are free to keep it or override the category.
6. (Optional) Attach a supporting photo or PDF (max 2 MB).
7. Click **Submit Grievance**.
8. A confirmation screen appears showing your unique reference ID: `CMK-2026-XXXXXX`. Click **Copy Reference ID**.

### Step 2: Track Progress
- **Anonymous Tracking:** Go to `/track` and paste `CMK-2026-XXXXXX` into the search box. View the department assignment, status badge, and public timeline.
- **Citizen Dashboard:** Go to `/citizen` to view your active complaints, resolution cards, and detailed timeline history.

### Step 3: Provide Feedback or Reopen
- Once the CMO accepts the department's action report and the status updates to **Resolved**:
  - Open the grievance detail view.
  - Fill out the **Citizen Feedback** card (1 to 5 star rating and comments).
  - If the problem recurs, click **Reopen Grievance**, explain what happened, and submit. The grievance moves to **Reopened** for CMO re-examination.

---

## 3. CMO Administrator Walkthrough

### Step 1: Monitor Queue & SLA Overdue Indicators
1. Log in as `cmo.admin@example.test`.
2. The CMO dashboard displays aggregate metrics:
   - **Total Grievances**, **Pending Review**, **Resolved**, and **SLA Overdue**.
   - Interactive breakdown charts by District, Department, Priority, and Status.
3. Use the filter bar to isolate `Submitted`, `Under Review`, or `Overdue` grievances.

### Step 2: Review AI Suggestions & Set Final Priority
1. Click on a grievance with status `Submitted`.
2. Inspect the **AI Triage Suggestion Panel**:
   - Review AI Summary, Suggested Department, and Confidence score.
3. Click **Review & Confirm**:
   - Select the final authoritative category and priority (High: 3-day SLA, Medium: 7-day, Low: 14-day).
   - The status transitions to **Under Review**, and `due_at` is recalculated.

### Step 3: Assign to Department & Officer
1. On the grievance detail page, click **Assign Department**.
2. Choose the responsible department (e.g. *Public Works*) and optionally a nodal officer (e.g. *Ravi Kumar*).
3. Add routing remarks and click **Confirm Assignment**.
4. The grievance transitions to **In Progress** with assignment state **Assigned**.

### Step 4: Escalate or Add Internal Remarks
- If a grievance is overdue or sensitive, click **Escalate**. This sets `escalated = true` and logs an internal remark visible only to CMO administrators.
- Use the **Add Administrative Remark** tool to add confidential internal notes or public citizen advisories.

### Step 5: Review Action-Taken Report (ATR)
1. When the department officer completes their work, the assignment state updates to **Report Submitted**.
2. Inspect the officer's report text and any uploaded evidence document.
3. Choose one of two actions:
   - **Accept Report:** Status changes to **Resolved**, assignment state changes to **Closed**, and the citizen sees the resolution on their tracker.
   - **Return for Rework:** Status stays **In Progress**, assignment state updates to **Returned**, and the officer is alerted to conduct additional site inspection.

---

## 4. Department Officer Walkthrough

### Step 1: Access Assigned Departmental Work
1. Log in as `officer.pwd@example.test` (password: `Demo@123`).
2. The Officer workspace displays **only** grievances routed to the officer's department (*Public Works*).
3. Grievances belonging to other departments are inaccessible (enforced by server-side RBAC).

### Step 2: Record Progress Updates
1. Click on an active grievance.
2. In the **Add Progress Remark** form, type investigation updates (e.g. *"Site inspection completed; raw materials ordered for culvert rebuilding"*).
3. Click **Save Progress**. The update appears immediately in the audit timeline.

### Step 3: Submit Action-Taken Report (ATR)
1. Once repairs or administrative actions are complete, navigate to the **Action-Taken Report** section.
2. Describe the completed remediation:
   > *"Reconstruction of road culvert completed on 17 Nov 2026. Tarring finished and traffic restored. Service inspected by junior engineer."*
3. (Optional) Attach a completion photo or signed inspection PDF.
4. Click **Submit Action Report**.
5. The assignment state updates to **Report Submitted** and moves to the CMO's desk for final sign-off.
