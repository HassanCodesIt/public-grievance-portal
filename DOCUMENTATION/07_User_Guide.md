# 07. User Guide

> **Recruitment prototype.** Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional. Please do not enter real personal information or real complaints.

This guide explains how citizens, CMO administrators and department officers use Janasevanam (ജനസേവനം). Demo login details are in the root `README.md`.

---

## 1. Before you start

- **First load can be slow.** The application is hosted on a free service that may sleep when idle. If the page seems stuck, wait up to a minute; a message says the server is waking up.
- **Use the demo accounts.** Test accounts exist for a citizen, a CMO administrator and department officers. You can also register your own citizen account.
- **Statuses.** Every grievance is in one of five statuses:

| Status | Meaning |
|---|---|
| Submitted | The citizen has submitted it; waiting for CMO review |
| Under Review | The CMO is reviewing it |
| In Progress | It has been forwarded to a department and the officer is working on it |
| Resolved | The CMO accepted the department's action-taken report |
| Reopened | The citizen reopened a resolved grievance; it goes back to CMO review |

- **AI suggestions.** Wherever you see "AI suggestion", it is only a recommendation. You can change it, and the CMO makes the final decision.

---

## 2. Everyone: public pages

| Page | What you can do |
|---|---|
| Home | Read the introduction, see sample statistics and featured departments, and use the Submit Grievance and Track Grievance buttons |
| About Us | Read the purpose, vision, mission and objectives |
| How It Works | See the steps from submission to resolution |
| Departments | Browse the sample departments |
| Contact Us | Send a message with your name, email, subject and message. It is saved for the administrators |
| FAQ | Read answers to common questions |
| Track Grievance | Enter a reference number to see the status, department and public history. No login needed |

---

## 3. Citizen guide

### 3.1 Register and log in
1. Choose **Register**.
2. Enter your full name, email, a 10-digit mobile number and a password (at least 8 characters), then confirm the password.
3. Log in with your email and password. You land on your dashboard.
4. Use the user menu to **log out** when you finish.

### 3.2 Submit a grievance
1. Choose **Submit Grievance**.
2. Select your **district** and a **category**.
3. Write a short **subject** and a detailed **description** (up to 2000 characters).
4. Optionally click **Get AI suggestion**. The assistant proposes a category, department, priority and a summary. Read it, and change the category if it is wrong. The label tells you whether it came from the AI model or from the keyword fallback.
5. Optionally attach one image or document (JPG, PNG or PDF, up to 2 MB).
6. Click **Submit**.
7. Save the **reference number** shown (for example `CMK-2026-000123`). Use the copy button, and keep it to track your grievance.

### 3.3 Track a grievance
- Without logging in: open **Track Grievance**, enter the reference number and read the status, the assigned department and the history.
- Logged in: open your dashboard and click the grievance for full details.

### 3.4 Your dashboard
- Cards show how many grievances you submitted, how many are pending and how many are resolved.
- The list shows each grievance with its status. Click one to see the complaint, the attachment, the department, the public remarks from the CMO and officers, and the history timeline.

### 3.5 Feedback and reopening
- When a grievance is **Resolved**, a feedback form appears. Give a rating from 1 to 5 stars and an optional comment. Feedback can be given once.
- If the problem is not really fixed, click **Reopen grievance** and explain why. The status becomes Reopened and the CMO reviews it again.

---

## 4. CMO administrator guide

### 4.1 Log in and read the overview
Log in with the CMO account. The overview shows:
- Count cards: **total, pending, resolved and overdue** grievances
- Charts: grievances by district, by department and by status, and a trend over time (all from stored data)
- A table of all grievances

### 4.2 Find grievances
Use the filters for **district, category, priority and status**, the overdue toggle, or search by reference number. Click **Reset** to clear the filters.

### 4.3 Open a grievance
Click a row to open the grievance. You will see:
1. The complaint, the citizen's name, and any attachments (click to view or download)
2. The **AI analysis**: summary, suggested category, department and priority, the confidence, the source label and any possible duplicates
3. The history timeline with every change, who made it and when, and whether each remark is public or internal

### 4.4 Review the AI suggestion
1. Read the AI summary and suggestions.
2. Click **Accept**, or **Override** and choose the final category and priority.
3. Confirm to move the grievance to **Under Review**. The due date is set from the final priority (High 3 days, Medium 7, Low 14).

### 4.5 Forward to a department
1. Choose the **department** and then an **officer** of that department.
2. Optionally add instructions.
3. Click **Forward**. The status becomes **In Progress**.

### 4.6 Remarks and escalation
- **Add a remark** and choose **Public** (the citizen can see it) or **Internal** (only the CMO and officers can see it).
- For a delayed grievance, click **Escalate** and confirm. This marks it as escalated and records an internal remark. The status does not change.

### 4.7 Review the department's report
When the officer submits an action-taken report, it appears on the grievance:
- Click **Accept and mark Resolved** if the work is satisfactory. The status becomes **Resolved**, and the citizen sees the update.
- Click **Return for rework** and write a remark (required) if it is not. The grievance stays In Progress and the officer sees a banner asking for rework.

### 4.8 Statistics
Use the charts and counts for district-wise and department-wise views and to find overdue grievances.

---

## 5. Department officer guide

### 5.1 Log in and open your list
Log in with the officer account given to you. You see only grievances forwarded to **your department**, with due dates and an assignment state: **Assigned, Report Submitted, Returned or Closed**. Overdue items are highlighted.

### 5.2 Review a grievance
Open a grievance to read the complaint, view attachments and read the CMO's instructions and remarks that are visible to officers.

### 5.3 Add progress
Use the progress form to add an investigation remark. The status stays **In Progress** and the remark is recorded in the history. Choose whether the remark is public (visible to the citizen) or internal.

### 5.4 Submit an action-taken report
1. Write the report describing what was done.
2. Optionally attach a supporting file (JPG, PNG or PDF, up to 2 MB).
3. Click **Submit to CMO**. The assignment state becomes **Report Submitted**.
4. The CMO reviews it. If it is accepted, the grievance becomes Resolved. If it is returned, a banner shows the CMO's remark, and you can update and submit the report again.

---

## 6. Typical journey at a glance

1. Citizen submits a grievance and receives a reference number.
2. CMO reviews it and confirms or changes the AI suggestions.
3. CMO forwards it to a department and officer.
4. Officer investigates, adds remarks and submits an action-taken report.
5. CMO reviews the report: accepts it (Resolved) or returns it for rework.
6. Citizen sees the update, gives feedback or reopens the grievance.

---

## 7. Help and troubleshooting

| Problem | What to do |
|---|---|
| The page is slow on the first visit | Wait up to a minute and refresh; the free host was asleep |
| "AI suggestion" says keyword fallback | The AI service was unavailable. You can still submit; the CMO will review it |
| My upload was rejected | Use a JPG, PNG or PDF of at most 2 MB |
| I cannot open a grievance | You can only open your own grievances (citizen) or your own department's (officer) |
| I forgot my reference number | Log in and open your dashboard; all your grievances are listed there |
| I cannot give feedback | Feedback is available only after the grievance is Resolved, and only once |
| I cannot reopen | Only Resolved grievances can be reopened |

## 8. Privacy and prototype notice

This is a recruitment prototype. Use fictional text only, and do not enter real names, phone numbers, addresses or real complaints. Nothing here is connected to, authorised by or endorsed by the Government of Kerala or the Chief Minister's Office.
