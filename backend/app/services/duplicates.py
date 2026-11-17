from datetime import datetime, timedelta
import difflib
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Grievance


def find_duplicate_candidates(
    db: Session,
    description: str,
    district: Optional[str] = None,
    category: Optional[str] = None,
    exclude_id: Optional[int] = None,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """Find potential duplicate grievances from recent open grievances using sequence similarity."""
    if not description or len(description.strip()) < 15:
        return []

    cutoff = datetime.utcnow() - timedelta(days=60)
    query = db.query(Grievance).filter(
        Grievance.created_at >= cutoff,
        Grievance.status != "Resolved",
    )

    if district:
        query = query.filter(Grievance.district == district)
    if category:
        query = query.filter(Grievance.category == category)
    if exclude_id:
        query = query.filter(Grievance.id != exclude_id)

    recent_grievances = query.limit(50).all()
    candidates = []

    target_text = description.strip().lower()

    for g in recent_grievances:
        cand_text = (g.subject + " " + g.description).strip().lower()
        matcher = difflib.SequenceMatcher(None, target_text, cand_text)
        ratio = matcher.ratio()

        if ratio >= 0.50:  # 50% or more similarity
            candidates.append({
                "id": g.id,
                "reference_no": g.reference_no,
                "subject": g.subject,
                "district": g.district,
                "category": g.category,
                "status": g.status,
                "similarity": round(ratio * 100, 1),
            })

    candidates.sort(key=lambda x: x["similarity"], reverse=True)
    return candidates[:limit]

