from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db import get_db
from ..models import Department, ContactEnquiry, Grievance, GrievanceHistory
from ..schemas import (
    DepartmentResponse,
    ContactCreate,
    ContactResponse,
    DISTRICTS,
    CATEGORIES,
    STATUSES,
)
from ..services.stats import get_public_portal_stats

router = APIRouter(tags=["Public"])


@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    """List all official government departments."""
    return db.query(Department).order_by(Department.name.asc()).all()


@router.get("/stats/public")
def public_stats(db: Session = Depends(get_db)):
    """Public dashboard summary counters."""
    return get_public_portal_stats(db)


@router.get("/meta")
def get_metadata():
    """Retrieve metadata values for districts, categories, and workflow statuses."""
    return {
        "districts": DISTRICTS,
        "categories": CATEGORIES,
        "statuses": STATUSES,
    }


@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact(enquiry_in: ContactCreate, db: Session = Depends(get_db)):
    """Submit a public contact enquiry stored in the database."""
    item = ContactEnquiry(
        name=enquiry_in.name.strip(),
        email=enquiry_in.email.strip().lower(),
        subject=enquiry_in.subject.strip(),
        message=enquiry_in.message.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/track/{reference_no}")
def track_grievance(reference_no: str, db: Session = Depends(get_db)):
    """
    Public tracking by Reference ID.
    Safety rule: returns NO personal data (names/phones/emails) and ONLY public history remarks.
    """
    clean_ref = reference_no.strip().upper()
    grievance = db.query(Grievance).filter(
        func_upper := Grievance.reference_no.ilike(clean_ref)
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No grievance found with reference ID '{reference_no}'.",
        )

    # Filter history entries to strictly PUBLIC visibility
    public_history = [
        {
            "timestamp": h.created_at.isoformat(),
            "actorName": h.actor_role,  # Anonymized for public view
            "actorRole": h.actor_role,
            "fromStatus": h.from_status,
            "toStatus": h.to_status,
            "remark": h.remark,
            "visibility": "Public",
        }
        for h in grievance.history
        if h.visibility == "Public"
    ]

    return {
        "id": str(grievance.id),
        "referenceNo": grievance.reference_no,
        "district": grievance.district,
        "category": grievance.category,
        "subject": grievance.subject,
        "description": grievance.description,
        "status": grievance.status,
        "priority": grievance.priority,
        "department": grievance.department.name if grievance.department else "Under CMO Review",
        "createdAt": grievance.created_at.isoformat(),
        "updatedAt": grievance.updated_at.isoformat(),
        "history": public_history,
    }
