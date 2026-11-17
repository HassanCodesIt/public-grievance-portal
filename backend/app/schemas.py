from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
    "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
]

CATEGORIES = [
    "Roads and Infrastructure", "Healthcare", "Education", "Water Supply",
    "Electricity", "Waste and Sanitation", "Public Distribution",
    "Land and Revenue", "Transport", "Other"
]

STATUSES = ["Submitted", "Under Review", "In Progress", "Resolved", "Reopened"]
PRIORITIES = ["Low", "Medium", "High"]
ROLES = ["citizen", "cmo_admin", "officer"]

INDIAN_MOBILE_REGEX = r"^[6-9]\d{9}$"
EMAIL_REGEX = r"^[\w\.\+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z0-9]{2,}$"

def validate_email_format(v: str) -> str:
    cleaned = v.strip().lower()
    if not re.match(EMAIL_REGEX, cleaned):
        raise ValueError("Invalid email format.")
    return cleaned

class ErrorResponse(BaseModel):
    detail: str
    code: str = "ERROR"

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    mobile: str = Field(..., description="10-digit Indian mobile number")
    password: str = Field(..., min_length=6)
    role: Optional[str] = "citizen"
    department_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-]", "", v)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]
        if not re.match(INDIAN_MOBILE_REGEX, cleaned):
            raise ValueError("Mobile number must be a valid 10-digit Indian phone number starting with 6-9.")
        return cleaned

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> str:
        if v and v not in ROLES:
            raise ValueError(f"Role must be one of: {', '.join(ROLES)}")
        return v or "citizen"

class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    mobile: str
    role: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    is_featured: bool

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=3000)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)

class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime

class AiAnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=2000)
    district: Optional[str] = None

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in DISTRICTS:
            return None
        return v

class AiAnalyzeResponse(BaseModel):
    category: str
    department: str
    priority: str
    summary: str
    confidence: float
    reasoning: str
    source: str
    model: str
    duplicate_candidates: List[dict] = []

class GrievanceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_status: Optional[str] = None
    to_status: str
    remark: str
    visibility: str
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    actor_role: str
    created_at: datetime
    # Frontend aliases
    timestamp: Optional[str] = None
    actorRole: Optional[str] = None
    actorName: Optional[str] = None
    fromStatus: Optional[str] = None
    toStatus: Optional[str] = None

class AttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    size: int
    kind: str
    created_at: datetime

class ActionReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_id: int
    text: str
    submitted_by: int
    submitted_by_name: Optional[str] = None
    submitted_at: datetime
    cmo_decision: Optional[str] = None
    cmo_remark: Optional[str] = None
    decided_at: Optional[datetime] = None

class GrievanceDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_no: str
    citizen_id: int
    citizen_name: str
    district: str
    category: str
    subject: str
    description: str
    priority: str
    status: str
    due_at: datetime
    is_overdue: bool
    escalated: bool
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    officer_name: Optional[str] = None
    ai_summary: Optional[str] = None
    assignment_state: str
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentResponse] = []
    history: List[GrievanceHistoryResponse] = []
    reports: List[ActionReportResponse] = []
    public_remarks: List[str] = []
    feedback: Optional[dict] = None
    
    # CamelCase aliases for frontend compatibility
    referenceNo: Optional[str] = None
    citizenName: Optional[str] = None
    dueAt: Optional[str] = None
    department: Optional[str] = None
    officer: Optional[str] = None
    aiSummary: Optional[str] = None
    assignmentState: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    publicRemarks: Optional[List[str]] = None

class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""

class ReopenCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)

class StatusTransitionRequest(BaseModel):
    status: str
    remark: str = Field(..., min_length=2)
    visibility: Optional[str] = "Public"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(STATUSES)}")
        return v

class CmoReviewRequest(BaseModel):
    category: str
    priority: str
    remark: Optional[str] = "Grievance reviewed and routed."

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}")
        return v

class CmoAssignRequest(BaseModel):
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    officer_id: Optional[int] = None
    officer_name: Optional[str] = None
    remark: Optional[str] = "Forwarded to department for action."

class CmoRemarkRequest(BaseModel):
    remark: str = Field(..., min_length=2)
    visibility: str = "Internal"

    @field_validator("visibility")
    @classmethod
    def validate_vis(cls, v: str) -> str:
        if v not in ["Public", "Internal"]:
            raise ValueError("Visibility must be either 'Public' or 'Internal'")
        return v

class CmoReportDecisionRequest(BaseModel):
    decision: str
    remark: Optional[str] = ""

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v.lower() not in ["accept", "return"]:
            raise ValueError("Decision must be either 'accept' or 'return'")
        return v.lower()

class OfficerProgressRequest(BaseModel):
    remark: str = Field(..., min_length=2)
    visibility: Optional[str] = "Public"

class OfficerActionReportRequest(BaseModel):
    text: str = Field(..., min_length=10)
