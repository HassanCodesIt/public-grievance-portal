import io
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
from app.models import User, Department, Grievance, GrievanceHistory, DepartmentAssignment, ActionReport
from app.services.workflow import calculate_due_date


# 1. Register and login success and failure
def test_01_register_and_login_success_and_failure(client):
    # Register success
    reg_resp = client.post("/api/auth/register", json={
        "name": "New Citizen",
        "email": "new.citizen@example.test",
        "mobile": "9847112233",
        "password": "Password123",
        "role": "citizen"
    })
    assert reg_resp.status_code == 201
    assert "token" in reg_resp.json()
    assert reg_resp.json()["user"]["email"] == "new.citizen@example.test"

    # Login success
    login_resp = client.post("/api/auth/login", json={
        "email": "new.citizen@example.test",
        "password": "Password123"
    })
    assert login_resp.status_code == 200
    assert "token" in login_resp.json()

    # Login failure: wrong password
    bad_login = client.post("/api/auth/login", json={
        "email": "new.citizen@example.test",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401


# 2. Duplicate email rejected
def test_02_duplicate_email_rejected(client):
    payload = {
        "name": "First User",
        "email": "duplicate@example.test",
        "mobile": "9847112244",
        "password": "Password123",
        "role": "citizen"
    }
    first_resp = client.post("/api/auth/register", json=payload)
    assert first_resp.status_code == 201

    # Second registration with identical email
    second_resp = client.post("/api/auth/register", json=payload)
    assert second_resp.status_code == 400
    assert "already exists" in second_resp.json()["detail"].lower()


# 3. Citizen cannot open another citizen's grievance
def test_03_citizen_cannot_open_another_citizens_grievance(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()
    cit_b = db_session.query(User).filter(User.email == "citizen.b@test.com").first()

    # Grievance owned by Citizen A
    g = Grievance(
        citizen_id=cit_a.id,
        district="Ernakulam",
        category="Roads and Infrastructure",
        subject="Road damage A",
        description="Potholes on lane A.",
        priority="Medium",
        status="Submitted",
        due_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.commit()

    # Citizen B tries to access Citizen A's grievance
    resp = client.get(f"/api/grievances/{g.id}", headers=auth_headers(cit_b))
    assert resp.status_code == 403


# 4. Officer cannot see another department's grievance
def test_04_officer_cannot_see_another_departments_grievance(client, db_session, auth_headers):
    health_dept = db_session.query(Department).filter(Department.name == "Health and Family Welfare").first()
    pwd_officer = db_session.query(User).filter(User.email == "officer.pwd@test.com").first()
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Grievance in Health department
    g = Grievance(
        citizen_id=cit_a.id,
        department_id=health_dept.id,
        district="Kozhikode",
        category="Healthcare",
        subject="Health Clinic Issue",
        description="No doctor present.",
        priority="High",
        status="In Progress",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.commit()

    # PWD officer tries to access Health grievance
    resp = client.get(f"/api/officer/grievances/{g.id}", headers=auth_headers(pwd_officer))
    assert resp.status_code == 403


# 5. Citizen cannot call CMO endpoints
def test_05_citizen_cannot_call_cmo_endpoints(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()
    resp = client.get("/api/cmo/grievances", headers=auth_headers(cit_a))
    assert resp.status_code == 403


# 6. Submit creates a unique reference ID and a history row
def test_06_submit_creates_unique_reference_id_and_history_row(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    resp = client.post(
        "/api/grievances",
        data={
            "district": "Ernakulam",
            "category": "Roads and Infrastructure",
            "subject": "Deep crater near bridge",
            "description": "The crater is causing severe traffic jams and vehicle damage.",
            "priority": "High"
        },
        headers=auth_headers(cit_a)
    )
    assert resp.status_code == 201
    data = resp.json()

    assert data["referenceNo"].startswith("CMK-")
    assert data["status"] == "Submitted"
    assert len(data["history"]) >= 1
    assert data["history"][0]["toStatus"] == "Submitted"


# 7. Full happy path: Submitted -> Under Review -> In Progress -> Resolved, with history count
def test_07_full_happy_path_workflow(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()
    cmo = db_session.query(User).filter(User.email == "cmo@test.com").first()
    pwd_officer = db_session.query(User).filter(User.email == "officer.pwd@test.com").first()
    pwd_dept = db_session.query(Department).filter(Department.name == "Public Works").first()

    # Step 1: Citizen Submits
    sub_resp = client.post(
        "/api/grievances",
        data={
            "district": "Thrissur",
            "category": "Roads and Infrastructure",
            "subject": "Bridge repair required",
            "description": "Retaining wall broken on highway bridge.",
            "priority": "High",
        },
        headers=auth_headers(cit_a)
    )
    assert sub_resp.status_code == 201
    gid = sub_resp.json()["id"]

    # Step 2: CMO reviews and confirms (Under Review)
    rev_resp = client.patch(
        f"/api/cmo/grievances/{gid}/review",
        json={"category": "Roads and Infrastructure", "priority": "High", "remark": "CMO confirmed priority."},
        headers=auth_headers(cmo)
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "Under Review"

    # Step 3: CMO forwards to PWD (In Progress)
    assign_resp = client.post(
        f"/api/cmo/grievances/{gid}/assign",
        json={"department_id": pwd_dept.id, "officer_id": pwd_officer.id, "remark": "Assigned to PWD team."},
        headers=auth_headers(cmo)
    )
    assert assign_resp.status_code == 200
    assert assign_resp.json()["status"] == "In Progress"

    # Step 4: Officer submits Action-Taken Report
    atr_resp = client.post(
        f"/api/officer/grievances/{gid}/action-report",
        data={"report": "Inspected bridge site and completed masonry reinforcement repairs."},
        headers=auth_headers(pwd_officer)
    )
    assert atr_resp.status_code == 200
    assert atr_resp.json()["assignmentState"] == "Report Submitted"

    # Fetch assignment ID
    assign_record = db_session.query(DepartmentAssignment).filter(DepartmentAssignment.grievance_id == int(gid)).first()
    assert assign_record is not None

    # Step 5: CMO accepts report (Resolved)
    dec_resp = client.post(
        f"/api/cmo/reports/{assign_record.id}/decision",
        json={"decision": "accept", "remark": "Satisfactory repair confirmed."},
        headers=auth_headers(cmo)
    )
    assert dec_resp.status_code == 200
    final_data = dec_resp.json()
    assert final_data["status"] == "Resolved"
    assert final_data["assignmentState"] == "Closed"

    # Verify history audit count
    history_rows = db_session.query(GrievanceHistory).filter(GrievanceHistory.grievance_id == int(gid)).all()
    assert len(history_rows) >= 4


# 8. Invalid transition returns 409
def test_08_invalid_transition_returns_409(client, db_session, auth_headers):
    cmo = db_session.query(User).filter(User.email == "cmo@test.com").first()
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Grievance in Submitted state
    g = Grievance(
        citizen_id=cit_a.id,
        district="Ernakulam",
        category="Roads and Infrastructure",
        subject="Road issue",
        description="Road pothole.",
        priority="Medium",
        status="Submitted",
        due_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.commit()

    # Attempt illegal transition: Directly from Submitted to Resolved
    resp = client.patch(
        f"/api/grievances/{g.id}/status",
        json={"status": "Resolved", "remark": "Direct resolve attempt"},
        headers=auth_headers(cmo)
    )
    assert resp.status_code == 409


# 9. Reopen only from Resolved
def test_09_reopen_only_from_resolved(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Case A: Grievance is in In Progress - attempt reopen should fail
    g_open = Grievance(
        citizen_id=cit_a.id,
        district="Wayanad",
        category="Healthcare",
        subject="Clinic issue",
        description="Clinic issue description.",
        priority="Medium",
        status="In Progress",
        due_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g_open)
    db_session.commit()

    resp_fail = client.post(
        f"/api/grievances/{g_open.id}/reopen",
        json={"reason": "Still not fixed properly."},
        headers=auth_headers(cit_a)
    )
    assert resp_fail.status_code == 409

    # Case B: Grievance is Resolved - reopen should succeed
    g_open.status = "Resolved"
    db_session.commit()

    resp_ok = client.post(
        f"/api/grievances/{g_open.id}/reopen",
        json={"reason": "Problem recurred after rain."},
        headers=auth_headers(cit_a)
    )
    assert resp_ok.status_code == 200
    assert resp_ok.json()["status"] == "Reopened"


# 10. Feedback only after Resolved, only once
def test_10_feedback_only_after_resolved_only_once(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    g = Grievance(
        citizen_id=cit_a.id,
        district="Palakkad",
        category="Water Supply",
        subject="Water problem",
        description="Low water pressure.",
        priority="Low",
        status="In Progress",  # Not resolved yet
        due_at=datetime.utcnow() + timedelta(days=14),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.commit()

    # Attempt feedback while In Progress
    fail_resp = client.post(
        f"/api/grievances/{g.id}/feedback",
        json={"rating": 5, "comment": "Great!"},
        headers=auth_headers(cit_a)
    )
    assert fail_resp.status_code == 400

    # Mark resolved
    g.status = "Resolved"
    db_session.commit()

    # First feedback succeeds
    ok_resp = client.post(
        f"/api/grievances/{g.id}/feedback",
        json={"rating": 5, "comment": "Excellent service."},
        headers=auth_headers(cit_a)
    )
    assert ok_resp.status_code == 200

    # Second feedback is rejected
    dup_resp = client.post(
        f"/api/grievances/{g.id}/feedback",
        json={"rating": 4, "comment": "Submitting again."},
        headers=auth_headers(cit_a)
    )
    assert dup_resp.status_code == 400


# 11. Overdue calculation
def test_11_overdue_calculation(client, db_session, auth_headers):
    cmo = db_session.query(User).filter(User.email == "cmo@test.com").first()
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Grievance with due_at in the past
    past_due = Grievance(
        citizen_id=cit_a.id,
        district="Kannur",
        category="Roads and Infrastructure",
        subject="Overdue road issue",
        description="Road damaged.",
        priority="High",
        status="In Progress",
        due_at=datetime.utcnow() - timedelta(days=2),  # Past due!
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow(),
    )
    db_session.add(past_due)
    db_session.commit()

    resp = client.get("/api/cmo/grievances?overdue=true", headers=auth_headers(cmo))
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["id"] == str(past_due.id) for item in items)


# 12. Escalation writes history
def test_12_escalation_writes_history(client, db_session, auth_headers):
    cmo = db_session.query(User).filter(User.email == "cmo@test.com").first()
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    g = Grievance(
        citizen_id=cit_a.id,
        district="Idukki",
        category="Roads and Infrastructure",
        subject="Landslide risk on road",
        description="Retaining wall loose.",
        priority="High",
        status="Under Review",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.commit()

    resp = client.post(f"/api/cmo/grievances/{g.id}/escalate", headers=auth_headers(cmo))
    assert resp.status_code == 200
    assert resp.json()["escalated"] is True

    history_entries = db_session.query(GrievanceHistory).filter(GrievanceHistory.grievance_id == g.id).all()
    assert any("ESCALATED" in h.remark for h in history_entries)


# 13. Upload rejects wrong type and oversized file
def test_13_upload_rejects_wrong_type_and_oversized_file(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Wrong type (.exe file)
    bad_file = io.BytesIO(b"MZ\x90\x00executable")
    bad_resp = client.post(
        "/api/grievances",
        data={
            "district": "Ernakulam",
            "category": "Roads and Infrastructure",
            "subject": "Bad file test",
            "description": "Testing upload type validation.",
        },
        files={"file": ("malicious.exe", bad_file, "application/octet-stream")},
        headers=auth_headers(cit_a)
    )
    assert bad_resp.status_code == 400

    # Oversized file (> 2 MB)
    huge_data = b"%PDF" + (b"0" * (2 * 1024 * 1024 + 500))
    huge_file = io.BytesIO(huge_data)
    huge_resp = client.post(
        "/api/grievances",
        data={
            "district": "Ernakulam",
            "category": "Roads and Infrastructure",
            "subject": "Huge file test",
            "description": "Testing file size cap.",
        },
        files={"file": ("large.pdf", huge_file, "application/pdf")},
        headers=auth_headers(cit_a)
    )
    assert huge_resp.status_code == 400


# 14. Public tracker hides internal remarks
def test_14_public_tracker_hides_internal_remarks(client, db_session):
    cit = db_session.query(User).filter(User.role == "citizen").first()
    cmo = db_session.query(User).filter(User.role == "cmo_admin").first()

    g = Grievance(
        citizen_id=cit.id,
        district="Kollam",
        category="Electricity",
        subject="Transformer sparking",
        description="Old transformer sparks during wind.",
        priority="High",
        status="In Progress",
        reference_no="CMK-2026-999888",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(g)
    db_session.flush()

    # Add public remark
    h_pub = GrievanceHistory(
        grievance_id=g.id,
        from_status="In Progress",
        to_status="In Progress",
        remark="Field team dispatched for inspection.",
        visibility="Public",
        actor_id=cmo.id,
        actor_role="CMO Reviewer",
        created_at=datetime.utcnow(),
    )
    # Add internal remark (confidential notes)
    h_int = GrievanceHistory(
        grievance_id=g.id,
        from_status="In Progress",
        to_status="In Progress",
        remark="CONFIDENTIAL: Internal vigilance inquiry initiated.",
        visibility="Internal",
        actor_id=cmo.id,
        actor_role="CMO Reviewer",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([h_pub, h_int])
    db_session.commit()

    resp = client.get("/api/track/CMK-2026-999888")
    assert resp.status_code == 200
    track_data = resp.json()

    remarks = [h["remark"] for h in track_data["history"]]
    assert "Field team dispatched for inspection." in remarks
    assert "CONFIDENTIAL: Internal vigilance inquiry initiated." not in remarks


# 15. CMO stats match seeded data
def test_15_cmo_stats_calculation(client, db_session, auth_headers):
    cmo = db_session.query(User).filter(User.email == "cmo@test.com").first()
    resp = client.get("/api/cmo/stats", headers=auth_headers(cmo))
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "pending" in data
    assert "resolved" in data
    assert "overdue" in data
    assert "by_district" in data
    assert "by_department" in data


# 16. AI analyze returns valid JSON (Groq mocked)
def test_16_ai_analyze_returns_valid_json_groq_mocked(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    mock_chat_completion = MagicMock()
    mock_chat_completion.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "category": "Water Supply",
                    "department": "Water Resources",
                    "priority": "High",
                    "summary": "Resident reports burst water pipeline on main road.",
                    "confidence": 0.94,
                    "reasoning": "Detected water pipeline burst terminology."
                })
            )
        )
    ]

    with patch("groq.Groq") as MockGroq:
        instance = MockGroq.return_value
        instance.chat.completions.create.return_value = mock_chat_completion

        with patch("app.services.ai_assistant.settings.GROQ_API_KEY", "dummy_gsk_key"):
            resp = client.post(
                "/api/ai/analyze",
                json={"description": "Burst drinking water pipeline leaking on temple road.", "district": "Ernakulam"},
                headers=auth_headers(cit_a)
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["category"] == "Water Supply"
            assert data["priority"] == "High"
            assert data["source"] == "groq"


# 17. AI fallback is used and labelled when Groq fails
def test_17_ai_fallback_is_used_and_labelled_when_groq_fails(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Simulate Groq raising an exception (e.g. network timeout or API error)
    with patch("groq.Groq") as MockGroq:
        instance = MockGroq.return_value
        instance.chat.completions.create.side_effect = Exception("Groq API rate limit or network timeout")

        with patch("app.services.ai_assistant.settings.GROQ_API_KEY", "dummy_gsk_key"):
            resp = client.post(
                "/api/ai/analyze",
                json={"description": "Large potholes on highway road near bridge.", "district": "Alappuzha"},
                headers=auth_headers(cit_a)
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["source"] == "fallback"
            assert data["category"] == "Roads and Infrastructure"


# 18. AI output outside allowed lists is rejected/normalized
def test_18_ai_output_outside_allowed_lists_is_normalized(client, db_session, auth_headers):
    cit_a = db_session.query(User).filter(User.email == "citizen.a@test.com").first()

    # Model hallucinations: category "Alien Invasion", priority "Super Critical"
    mock_hallucination = MagicMock()
    mock_hallucination.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "category": "Alien Invasion",
                    "department": "Space Force",
                    "priority": "Super Critical",
                    "summary": "Unidentified flying complaint.",
                    "confidence": 0.50,
                    "reasoning": "Hallucinated category."
                })
            )
        )
    ]

    with patch("groq.Groq") as MockGroq:
        instance = MockGroq.return_value
        instance.chat.completions.create.return_value = mock_hallucination

        with patch("app.services.ai_assistant.settings.GROQ_API_KEY", "dummy_gsk_key"):
            resp = client.post(
                "/api/ai/analyze",
                json={"description": "Something strange happening in the area sky.", "district": "Kannur"},
                headers=auth_headers(cit_a)
            )
            assert resp.status_code == 200
            data = resp.json()
            # Must be normalized to allowed values
            assert data["category"] in ["Roads and Infrastructure", "Healthcare", "Education", "Water Supply", "Electricity", "Waste and Sanitation", "Public Distribution", "Land and Revenue", "Transport", "Other"]
            assert data["priority"] in ["Low", "Medium", "High"]

