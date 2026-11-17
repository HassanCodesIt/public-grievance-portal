from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..db import get_db
from ..models import (
    Grievance,
    User,
    Department,
    DepartmentAssignment,
    ActionReport,
    AiAnalysis,
)
from ..schemas import (
    CmoReviewRequest,
    CmoAssignRequest,
    CmoRemarkRequest,
    CmoReportDecisionRequest,
)
from ..security import require_role
from ..services.workflow import transition, add_history_entry, calculate_due_date
from ..services.stats import get_cmo_dashboard_stats
from .grievances import serialize_grievance_for_response

router = APIRouter(prefix="/cmo", tags=["CMO Administration"])


@router.get("/grievances")
def list_cmo_grievances(
    status: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    overdue: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """
    CMO administration grievance queue with advanced filtering and pagination.
    """
    query = db.query(Grievance)

    if status:
        query = query.filter(Grievance.status == status)
    if district:
        query = query.filter(Grievance.district == district)
    if category:
        query = query.filter(Grievance.category == category)
    if priority:
        query = query.filter(Grievance.priority == priority)
    if overdue is not None:
        now = datetime.utcnow()
        if overdue:
            query = query.filter(Grievance.status != "Resolved", Grievance.due_at < now)
        else:
            query = query.filter(or_(Grievance.status == "Resolved", Grievance.due_at >= now))

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Grievance.reference_no.ilike(s),
                Grievance.subject.ilike(s),
                Grievance.description.ilike(s),
            )
        )

    total = query.count()
    items = (
        query.order_by(Grievance.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    serialized = [serialize_grievance_for_response(g, include_internal_history=True) for g in items]
    return {
        "items": serialized,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/grievances/{id}")
def get_cmo_grievance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """Get full grievance record including internal remarks, AI analyses, and assignment history."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    res = serialize_grievance_for_response(grievance, include_internal_history=True)

    # Attach AI analyses records
    analyses = (
        db.query(AiAnalysis)
        .filter(AiAnalysis.grievance_id == grievance.id)
        .order_by(AiAnalysis.created_at.desc())
        .all()
    )
    res["aiAnalyses"] = [
        {
            "id": a.id,
            "category": a.category,
            "department": a.department,
            "priority": a.priority,
            "summary": a.summary,
            "confidence": a.confidence,
            "reasoning": a.reasoning,
            "source": a.source,
            "model": a.model,
            "final_category": a.final_category,
            "final_priority": a.final_priority,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]

    return res


@router.patch("/grievances/{id}/review")
def review_grievance(
    id: int,
    payload: CmoReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """
    CMO reviews AI suggestions, sets final human-confirmed category and priority,
    moves grievance status to 'Under Review'.
    """
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    # Record review decision on latest AiAnalysis row
    latest_analysis = (
        db.query(AiAnalysis)
        .filter(AiAnalysis.grievance_id == grievance.id)
        .order_by(AiAnalysis.created_at.desc())
        .first()
    )
    if latest_analysis:
        latest_analysis.final_category = payload.category
        latest_analysis.final_priority = payload.priority
        latest_analysis.reviewed_by = current_user.id

    updated = transition(
        db=db,
        grievance=grievance,
        to_status="Under Review",
        actor=current_user,
        remark=payload.remark or f"CMO confirmed category as '{payload.category}' and priority as '{payload.priority}'.",
        visibility="Public",
        category=payload.category,
        priority=payload.priority,
    )

    return serialize_grievance_for_response(updated, include_internal_history=True)


@router.post("/grievances/{id}/assign")
def assign_grievance(
    id: int,
    payload: CmoAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """
    CMO forwards grievance to a department and specific officer.
    Transitions grievance to 'In Progress' and sets assignment state to 'Assigned'.
    """
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    dept_id = payload.department_id
    if not dept_id and payload.department_name:
        dept = db.query(Department).filter(Department.name == payload.department_name).first()
        if dept:
            dept_id = dept.id

    if not dept_id:
        dept_id = grievance.department_id

    if not dept_id:
        raise HTTPException(status_code=400, detail="Department ID or department name required.")

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=400, detail="Department does not exist.")

    officer_id = payload.officer_id
    if not officer_id and payload.officer_name:
        off = db.query(User).filter(User.name == payload.officer_name, User.role == "officer").first()
        if off:
            officer_id = off.id

    remark = payload.remark or f"Forwarded to {dept.name} for departmental action."

    updated = transition(
        db=db,
        grievance=grievance,
        to_status="In Progress",
        actor=current_user,
        remark=remark,
        visibility="Public",
        department_id=dept_id,
        officer_id=officer_id,
    )

    return serialize_grievance_for_response(updated, include_internal_history=True)


@router.post("/grievances/{id}/remarks")
def add_cmo_remark(
    id: int,
    payload: CmoRemarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """Add a public or internal administrative remark without changing status."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    add_history_entry(
        db=db,
        grievance=grievance,
        from_status=grievance.status,
        to_status=grievance.status,
        remark=payload.remark.strip(),
        actor=current_user,
        visibility=payload.visibility,
    )
    db.commit()

    return {"id": id, "remark": payload.remark, "visibility": payload.visibility, "saved": True}


@router.post("/grievances/{id}/escalate")
def escalate_grievance(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """Escalate a delayed or sensitive grievance to priority attention."""
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    grievance.escalated = True
    add_history_entry(
        db=db,
        grievance=grievance,
        from_status=grievance.status,
        to_status=grievance.status,
        remark="Grievance marked as ESCALATED by CMO due to SLA delay or critical priority.",
        actor=current_user,
        visibility="Internal",
    )
    db.commit()
    db.refresh(grievance)

    return serialize_grievance_for_response(grievance, include_internal_history=True)


@router.post("/reports/{assignment_id}/decision")
def decide_action_report(
    assignment_id: int,
    payload: CmoReportDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """
    CMO accepts (moves grievance to 'Resolved') or returns an officer's action-taken report for rework.
    """
    assignment = db.query(DepartmentAssignment).filter(DepartmentAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Department assignment not found.")

    report = (
        db.query(ActionReport)
        .filter(ActionReport.assignment_id == assignment.id)
        .order_by(ActionReport.submitted_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=400, detail="No action-taken report has been submitted for this assignment yet.")

    grievance = assignment.grievance

    if payload.decision == "accept":
        report.cmo_decision = "accept"
        report.cmo_remark = payload.remark or "Action report accepted. Grievance resolved."
        report.decided_at = datetime.utcnow()
        assignment.state = "Closed"

        updated = transition(
            db=db,
            grievance=grievance,
            to_status="Resolved",
            actor=current_user,
            remark=payload.remark or "Department action report reviewed and confirmed. Grievance marked as Resolved.",
            visibility="Public",
        )
    else:  # return for rework
        report.cmo_decision = "return"
        report.cmo_remark = payload.remark or "Report returned for further inspection and rework."
        report.decided_at = datetime.utcnow()
        assignment.state = "Returned"

        updated = transition(
            db=db,
            grievance=grievance,
            to_status="In Progress",
            actor=current_user,
            remark=f"Action report returned for rework: {payload.remark or 'Additional details needed'}.",
            visibility="Public",
        )

    db.commit()
    return serialize_grievance_for_response(updated, include_internal_history=True)


@router.get("/stats")
def cmo_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin"])),
):
    """Detailed analytics and counts for CMO Admin dashboard."""
    return get_cmo_dashboard_stats(db)

