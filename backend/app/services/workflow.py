from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Grievance, GrievanceHistory, DepartmentAssignment, User, ActionReport

# Priority SLA in days
PRIORITY_SLA_DAYS = {
    "High": 3,
    "Medium": 7,
    "Low": 14,
}

def calculate_due_date(priority: str, from_date: Optional[datetime] = None) -> datetime:
    """Compute due date based on SLA for priority."""
    base = from_date or datetime.utcnow()
    days = PRIORITY_SLA_DAYS.get(priority, 7)
    return base + timedelta(days=days)


def generate_reference_no(db: Session, grievance_id: int) -> str:
    """Format reference ID as CMK-YYYY-XXXXXX."""
    year = datetime.utcnow().year
    return f"CMK-{year}-{grievance_id:06d}"


def add_history_entry(
    db: Session,
    grievance: Grievance,
    from_status: Optional[str],
    to_status: str,
    remark: str,
    actor: User,
    visibility: str = "Public",
) -> GrievanceHistory:
    """Record a history audit trail entry."""
    entry = GrievanceHistory(
        grievance_id=grievance.id,
        from_status=from_status,
        to_status=to_status,
        remark=remark,
        visibility=visibility,
        actor_id=actor.id,
        actor_name=actor.name,
        actor_role=actor.role if actor.role != "cmo_admin" else "CMO Reviewer",
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    return entry


def validate_transition(current_status: str, target_status: str, role: str) -> bool:
    """Check if the transition is permissible according to the portal state machine."""
    # CMO transitions
    if role == "cmo_admin":
        if current_status == "Submitted" and target_status == "Under Review":
            return True
        if current_status == "Under Review" and target_status == "In Progress":
            return True
        if current_status == "In Progress" and target_status in ("In Progress", "Resolved"):
            return True
        if current_status == "Reopened" and target_status == "Under Review":
            return True
        # Escalation does not change status
        if current_status == target_status:
            return True

    # Officer transitions
    elif role == "officer":
        if current_status == "In Progress" and target_status == "In Progress":
            return True

    # Citizen transitions
    elif role == "citizen":
        if current_status == "Resolved" and target_status == "Reopened":
            return True

    return False


def transition(
    db: Session,
    grievance: Grievance,
    to_status: str,
    actor: User,
    remark: str,
    visibility: str = "Public",
    category: Optional[str] = None,
    priority: Optional[str] = None,
    department_id: Optional[int] = None,
    officer_id: Optional[int] = None,
) -> Grievance:
    """Enforce state machine transition and record audit history row."""
    from_status = grievance.status

    if not validate_transition(from_status, to_status, actor.role):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid transition from '{from_status}' to '{to_status}' by role '{actor.role}'.",
        )

    # Apply state change
    grievance.status = to_status
    grievance.updated_at = datetime.utcnow()

    # Recompute priority and due date if priority changed
    if priority and priority != grievance.priority:
        grievance.priority = priority
        grievance.due_at = calculate_due_date(priority, grievance.created_at)

    if category:
        grievance.category = category

    if department_id:
        grievance.department_id = department_id

    # Create assignment if moving from Under Review to In Progress or reassigned
    if to_status == "In Progress" and (department_id or officer_id or from_status == "Under Review"):
        assign_dept_id = department_id or grievance.department_id
        if assign_dept_id:
            assignment = DepartmentAssignment(
                grievance_id=grievance.id,
                department_id=assign_dept_id,
                officer_id=officer_id,
                assigned_by=actor.id,
                state="Assigned",
                assigned_at=datetime.utcnow(),
            )
            db.add(assignment)

    # Add history log
    add_history_entry(
        db=db,
        grievance=grievance,
        from_status=from_status,
        to_status=to_status,
        remark=remark,
        actor=actor,
        visibility=visibility,
    )

    db.commit()
    db.refresh(grievance)
    return grievance

