import hashlib
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    Grievance,
    User,
    Attachment,
    CitizenFeedback,
    AiAnalysis,
    Department,
)
from ..schemas import (
    FeedbackCreate,
    ReopenCreate,
    DISTRICTS,
    CATEGORIES,
    PRIORITIES,
)
from ..security import get_current_user, require_role
from ..services.workflow import calculate_due_date, generate_reference_no, add_history_entry, transition
from ..services.uploads import validate_and_read_upload
from ..services.ai_assistant import analyze_grievance_with_ai

router = APIRouter(prefix="/grievances", tags=["Citizen Grievances"])


def serialize_grievance_for_response(g: Grievance, include_internal_history: bool = False) -> dict:
    """Format grievance model into dictionary compatible with both API schema and frontend."""
    now = datetime.utcnow()
    is_overdue = g.status != "Resolved" and g.due_at < now

    # Filter history by visibility if requested
    history_entries = []
    public_remarks = []
    for h in g.history:
        if include_internal_history or h.visibility == "Public":
            history_entries.append({
                "id": h.id,
                "timestamp": h.created_at.isoformat(),
                "actorName": h.actor_name or h.actor_role,
                "actorRole": h.actor_role,
                "fromStatus": h.from_status,
                "toStatus": h.to_status,
                "remark": h.remark,
                "visibility": h.visibility,
                "created_at": h.created_at.isoformat(),
            })
        if h.visibility == "Public" and h.remark:
            public_remarks.append(h.remark)

    # Active assignment state
    assignment_state = "Assigned"
    officer_name = None
    if g.assignments:
        latest = g.assignments[0]
        assignment_state = latest.state
        if latest.officer:
            officer_name = latest.officer.name

    # Attachments
    attachment_list = [
        {
            "id": att.id,
            "filename": att.filename,
            "content_type": att.content_type,
            "size": att.size,
            "kind": att.kind,
            "created_at": att.created_at.isoformat(),
        }
        for att in g.attachments
    ]

    # Action reports
    report_list = []
    latest_report_text = None
    for assign in g.assignments:
        for r in assign.reports:
            report_list.append({
                "id": r.id,
                "assignment_id": r.assignment_id,
                "text": r.text,
                "submitted_by": r.submitted_by,
                "submitted_by_name": r.submitter.name if r.submitter else None,
                "submitted_at": r.submitted_at.isoformat(),
                "cmo_decision": r.cmo_decision,
                "cmo_remark": r.cmo_remark,
                "decided_at": r.decided_at.isoformat() if r.decided_at else None,
            })
            if not latest_report_text:
                latest_report_text = r.text

    # Feedback
    feedback_data = None
    if g.feedback:
        feedback_data = {
            "id": g.feedback.id,
            "rating": g.feedback.rating,
            "comment": g.feedback.comment,
            "createdAt": g.feedback.created_at.isoformat(),
        }

    dept_name = g.department.name if g.department else "Pending CMO Review"

    return {
        "id": str(g.id),
        "referenceNo": g.reference_no or f"CMK-{g.id}",
        "reference_no": g.reference_no or f"CMK-{g.id}",
        "citizenId": g.citizen_id,
        "citizenName": g.citizen.name if g.citizen else "Anonymous",
        "district": g.district,
        "category": g.category,
        "subject": g.subject,
        "description": g.description,
        "priority": g.priority,
        "status": g.status,
        "dueAt": g.due_at.isoformat(),
        "due_at": g.due_at.isoformat(),
        "isOverdue": is_overdue,
        "is_overdue": is_overdue,
        "escalated": g.escalated,
        "department": dept_name,
        "department_id": g.department_id,
        "officer": officer_name,
        "aiSummary": g.ai_summary or "",
        "assignmentState": assignment_state,
        "assignment_state": assignment_state,
        "createdAt": g.created_at.isoformat(),
        "updatedAt": g.updated_at.isoformat(),
        "created_at": g.created_at.isoformat(),
        "updated_at": g.updated_at.isoformat(),
        "attachments": [att["filename"] for att in attachment_list],
        "attachmentDetails": attachment_list,
        "report": latest_report_text,
        "reports": report_list,
        "publicRemarks": public_remarks,
        "history": history_entries,
        "feedback": feedback_data,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_grievance(
    district: str = Form(...),
    category: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    priority: Optional[str] = Form("Medium"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Citizen submits a new grievance (multipart form).
    Generates reference ID, runs server-side AI analysis, and records history.
    """
    if district not in DISTRICTS:
        raise HTTPException(status_code=400, detail=f"Invalid district '{district}'.")
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category '{category}'.")
    if priority not in PRIORITIES:
        priority = "Medium"

    due_at = calculate_due_date(priority)

    # 1. Create grievance
    grievance = Grievance(
        citizen_id=current_user.id,
        district=district,
        category=category,
        subject=subject.strip(),
        description=description.strip(),
        priority=priority,
        status="Submitted",
        due_at=due_at,
        escalated=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(grievance)
    db.flush()  # obtain grievance.id

    # 2. Generate Reference ID
    grievance.reference_no = generate_reference_no(db, grievance.id)

    # 3. Server-side AI analysis execution & storage
    ai_result = analyze_grievance_with_ai(description=description, district=district)
    grievance.ai_summary = ai_result.get("summary")

    # Match suggested department to DB department
    sugg_dept_name = ai_result.get("department")
    sugg_dept = db.query(Department).filter(Department.name == sugg_dept_name).first()
    if sugg_dept:
        grievance.department_id = sugg_dept.id

    # Store analysis audit row
    input_hash = hashlib.sha256(description.strip().lower().encode("utf-8")).hexdigest()
    analysis_record = AiAnalysis(
        grievance_id=grievance.id,
        input_hash=input_hash,
        category=ai_result.get("category", category),
        department=sugg_dept_name or "Local Self Government",
        priority=ai_result.get("priority", priority),
        summary=ai_result.get("summary", ""),
        confidence=ai_result.get("confidence", 0.8),
        reasoning=ai_result.get("reasoning", ""),
        source=ai_result.get("source", "groq"),
        model=ai_result.get("model", "openai/gpt-oss-120b"),
        raw_json=ai_result.get("raw_json"),
        final_category=category,
        final_priority=priority,
    )
    db.add(analysis_record)

    # 4. Handle File Attachment
    if file and file.filename:
        filename, mime, size, data = validate_and_read_upload(file)
        attachment = Attachment(
            grievance_id=grievance.id,
            uploaded_by=current_user.id,
            kind="grievance",
            filename=filename,
            content_type=mime,
            size=size,
            data=data,
            created_at=datetime.utcnow(),
        )
        db.add(attachment)

    # 5. History row
    add_history_entry(
        db=db,
        grievance=grievance,
        from_status=None,
        to_status="Submitted",
        remark="Grievance submitted and reference number generated.",
        actor=current_user,
        visibility="Public",
    )

    db.commit()
    db.refresh(grievance)

    return serialize_grievance_for_response(grievance, include_internal_history=False)


@router.get("/mine")
def get_my_grievances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all grievances submitted by the logged-in citizen."""
    items = (
        db.query(Grievance)
        .filter(Grievance.citizen_id == current_user.id)
        .order_by(Grievance.created_at.desc())
        .all()
    )
    return [serialize_grievance_for_response(g, include_internal_history=False) for g in items]


@router.get("/{id}")
def get_grievance_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get grievance details with object-level authorization:
    - Citizen can view only their own
    - Officer can view only their department's
    - CMO can view any
    """
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if current_user.role == "citizen" and grievance.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this grievance.")

    if current_user.role == "officer":
        if grievance.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="Access denied: Grievance belongs to another department.")

    include_internal = current_user.role in ("cmo_admin", "officer")
    return serialize_grievance_for_response(grievance, include_internal_history=include_internal)


@router.post("/{id}/feedback")
def submit_feedback(
    id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit citizen rating & comments after grievance has been Resolved."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if grievance.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the grievance submitter can leave feedback.")

    if grievance.status != "Resolved":
        raise HTTPException(
            status_code=400,
            detail="Citizen feedback can only be submitted once the grievance is Resolved.",
        )

    if grievance.feedback:
        raise HTTPException(
            status_code=400,
            detail="Feedback has already been submitted for this grievance.",
        )

    fb = CitizenFeedback(
        grievance_id=grievance.id,
        rating=payload.rating,
        comment=payload.comment.strip() if payload.comment else None,
        created_at=datetime.utcnow(),
    )
    db.add(fb)
    db.commit()

    return {"id": id, "rating": payload.rating, "comment": payload.comment, "saved": True}


@router.post("/{id}/reopen")
def reopen_grievance(
    id: int,
    payload: ReopenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Citizen reopens a previously Resolved grievance with a justification reason."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if grievance.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the grievance owner can reopen it.")

    if grievance.status != "Resolved":
        raise HTTPException(
            status_code=409,
            detail=f"Cannot reopen grievance from status '{grievance.status}'. Grievances can only be reopened from 'Resolved'.",
        )

    updated = transition(
        db=db,
        grievance=grievance,
        to_status="Reopened",
        actor=current_user,
        remark=payload.reason.strip(),
        visibility="Public",
    )

    return serialize_grievance_for_response(updated, include_internal_history=False)


@router.get("/attachments/{id}/download")
@router.get("/attachments/{id}")
def download_attachment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download attachment with authorization:
    Allowed only for: grievance submitter, CMO admin, or assigned department officer.
    """
    attachment = db.query(Attachment).filter(Attachment.id == id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    grievance = attachment.grievance
    if not grievance:
        raise HTTPException(status_code=404, detail="Parent grievance not found.")

    # Authorization check
    is_owner = current_user.role == "citizen" and grievance.citizen_id == current_user.id
    is_cmo = current_user.role == "cmo_admin"
    is_assigned_officer = (
        current_user.role == "officer"
        and current_user.department_id == grievance.department_id
    )

    if not (is_owner or is_cmo or is_assigned_officer):
        raise HTTPException(status_code=403, detail="Not authorized to download this file.")

    return Response(
        content=attachment.data,
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{attachment.filename}"'
        },
    )

