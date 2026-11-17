from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Grievance, User
from ..schemas import StatusTransitionRequest
from ..security import require_role
from ..services.workflow import transition
from .grievances import serialize_grievance_for_response

router = APIRouter(prefix="/grievances", tags=["Status Workflow"])


@router.patch("/{id}/status")
def change_status(
    id: int,
    payload: StatusTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["cmo_admin", "officer"])),
):
    """
    Role-checked transition endpoint enforcing the grievance state machine.
    """
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    # Officer check: must belong to their department
    if current_user.role == "officer":
        if grievance.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Officers can only update grievances assigned to their department.",
            )

    updated = transition(
        db=db,
        grievance=grievance,
        to_status=payload.status,
        actor=current_user,
        remark=payload.remark,
        visibility=payload.visibility or "Public",
    )

    return serialize_grievance_for_response(updated, include_internal_history=True)
