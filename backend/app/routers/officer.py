from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    Grievance,
    User,
    DepartmentAssignment,
    ActionReport,
    Attachment,
)
from ..schemas import OfficerProgressRequest
from ..security import require_role
from ..services.workflow import add_history_entry
from ..services.uploads import validate_and_read_upload
from .grievances import serialize_grievance_for_response

router = APIRouter(prefix="/officer", tags=["Department Officers"])


@router.get("/grievances")
def list_officer_grievances(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["officer"])),
):
    """
    List only the grievances assigned to this officer's department.
    """
    if not current_user.department_id:
        return []

    items = (
        db.query(Grievance)
        .filter(Grievance.department_id == current_user.department_id)
        .order_by(Grievance.created_at.desc())
        .all()
    )

    return [serialize_grievance_for_response(g, include_internal_history=True) for g in items]


@router.get("/grievances/{id}")
def get_officer_grievance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["officer"])),
):
    """View grievance details assigned to this officer's department."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Grievance is assigned to another department.",
        )

    return serialize_grievance_for_response(grievance, include_internal_history=True)


@router.post("/grievances/{id}/progress")
def add_officer_progress(
    id: int,
    payload: OfficerProgressRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["officer"])),
):
    """Add progress or field investigation remarks to grievance history."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Grievance is assigned to another department.",
        )

    entry = add_history_entry(
        db=db,
        grievance=grievance,
        from_status=grievance.status,
        to_status=grievance.status,
        remark=payload.remark.strip(),
        actor=current_user,
        visibility=payload.visibility or "Public",
    )
    db.commit()

    return {"id": id, "remark": payload.remark, "saved": True}


@router.post("/grievances/{id}/action-report")
def submit_action_report(
    id: int,
    report: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["officer"])),
):
    """
    Department officer submits final Action-Taken Report (ATR) with optional supporting document.
    Updates assignment state to 'Report Submitted' for CMO review.
    """
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Grievance is assigned to another department.",
        )

    # Find or create latest assignment
    assignment = (
        db.query(DepartmentAssignment)
        .filter(
            DepartmentAssignment.grievance_id == grievance.id,
            DepartmentAssignment.department_id == current_user.department_id,
        )
        .order_by(DepartmentAssignment.assigned_at.desc())
        .first()
    )

    if not assignment:
        assignment = DepartmentAssignment(
            grievance_id=grievance.id,
            department_id=current_user.department_id,
            officer_id=current_user.id,
            assigned_by=current_user.id,
            state="Assigned",
            assigned_at=datetime.utcnow(),
        )
        db.add(assignment)
        db.flush()

    # Create Action Report record
    action_report = ActionReport(
        assignment_id=assignment.id,
        text=report.strip(),
        submitted_by=current_user.id,
        submitted_at=datetime.utcnow(),
    )
    db.add(action_report)

    # Update assignment state
    assignment.state = "Report Submitted"
    grievance.updated_at = datetime.utcnow()

    # Optional file attachment for action report
    if file and file.filename:
        filename, mime, size, data = validate_and_read_upload(file)
        att = Attachment(
            grievance_id=grievance.id,
            assignment_id=assignment.id,
            uploaded_by=current_user.id,
            kind="action_report",
            filename=filename,
            content_type=mime,
            size=size,
            data=data,
            created_at=datetime.utcnow(),
        )
        db.add(att)

    # Add audit trail entry
    add_history_entry(
        db=db,
        grievance=grievance,
        from_status=grievance.status,
        to_status=grievance.status,
        remark=f"Action-Taken Report submitted by {current_user.name} ({current_user.department.name if current_user.department else 'Officer'}). Awaiting CMO review.",
        actor=current_user,
        visibility="Public",
    )

    db.commit()
    db.refresh(grievance)

    return serialize_grievance_for_response(grievance, include_internal_history=True)
