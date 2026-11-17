from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import AiAnalyzeRequest, AiAnalyzeResponse
from ..security import get_current_user
from ..services.ai_assistant import analyze_grievance_with_ai
from ..services.duplicates import find_duplicate_candidates

router = APIRouter(prefix="/ai", tags=["AI Grievance Assistant"])


@router.post("/analyze", response_model=AiAnalyzeResponse)
def analyze_grievance(
    payload: AiAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI Grievance Assistant endpoint using Groq (openai/gpt-oss-120b) with labeled fallback.
    Suggests category, department, priority, and summary for human confirmation.
    """
    if len(payload.description.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grievance description must contain at least 10 characters for AI triage.",
        )

    # 1. Run AI / Fallback Analysis
    ai_result = analyze_grievance_with_ai(
        description=payload.description,
        district=payload.district,
    )

    # 2. Duplicate Detection
    duplicates = find_duplicate_candidates(
        db=db,
        description=payload.description,
        district=payload.district,
        category=ai_result.get("category"),
    )

    return {
        "category": ai_result["category"],
        "department": ai_result["department"],
        "priority": ai_result["priority"],
        "summary": ai_result["summary"],
        "confidence": ai_result["confidence"],
        "reasoning": ai_result["reasoning"],
        "source": ai_result["source"],
        "model": ai_result["model"],
        "duplicate_candidates": duplicates,
    }

