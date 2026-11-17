from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    LargeBinary,
)
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    mobile = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)  # 'citizen', 'cmo_admin', 'officer'
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="officers")
    grievances = relationship("Grievance", back_populates="citizen")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    is_featured = Column(Boolean, default=True, nullable=False)

    officers = relationship("User", back_populates="department")
    grievances = relationship("Grievance", back_populates="department")
    assignments = relationship("DepartmentAssignment", back_populates="department")


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    reference_no = Column(String(40), unique=True, index=True, nullable=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    district = Column(String(60), nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="Medium", index=True)  # Low, Medium, High
    status = Column(String(30), nullable=False, default="Submitted", index=True)  # Submitted, Under Review, In Progress, Resolved, Reopened
    due_at = Column(DateTime, nullable=False, index=True)
    escalated = Column(Boolean, default=False, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    citizen = relationship("User", back_populates="grievances")
    department = relationship("Department", back_populates="grievances")
    history = relationship("GrievanceHistory", back_populates="grievance", cascade="all, delete-orphan", order_by="GrievanceHistory.created_at.asc()")
    assignments = relationship("DepartmentAssignment", back_populates="grievance", cascade="all, delete-orphan", order_by="DepartmentAssignment.assigned_at.desc()")
    attachments = relationship("Attachment", back_populates="grievance", cascade="all, delete-orphan")
    feedback = relationship("CitizenFeedback", back_populates="grievance", uselist=False, cascade="all, delete-orphan")
    ai_analyses = relationship("AiAnalysis", back_populates="grievance")


class GrievanceHistory(Base):
    __tablename__ = "grievance_history"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False, index=True)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    remark = Column(Text, nullable=False)
    visibility = Column(String(20), nullable=False, default="Public")  # 'Public' or 'Internal'
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_name = Column(String(100), nullable=True)
    actor_role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    grievance = relationship("Grievance", back_populates="history")
    actor = relationship("User")


class DepartmentAssignment(Base):
    __tablename__ = "department_assignments"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(String(40), nullable=False, default="Assigned")  # Assigned, Report Submitted, Returned, Closed
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    officer = relationship("User", foreign_keys=[officer_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    reports = relationship("ActionReport", back_populates="assignment", cascade="all, delete-orphan", order_by="ActionReport.submitted_at.desc()")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False, index=True)
    assignment_id = Column(Integer, ForeignKey("department_assignments.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    kind = Column(String(30), nullable=False, default="grievance")  # 'grievance', 'action_report'
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="attachments")


class ActionReport(Base):
    __tablename__ = "action_reports"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("department_assignments.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cmo_decision = Column(String(30), nullable=True)  # 'accept', 'return'
    cmo_remark = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)

    assignment = relationship("DepartmentAssignment", back_populates="reports")
    submitter = relationship("User", foreign_keys=[submitted_by])


class CitizenFeedback(Base):
    __tablename__ = "citizen_feedback"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), unique=True, nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="feedback")


class ContactEnquiry(Base):
    __tablename__ = "contact_enquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AiAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=True, index=True)
    input_hash = Column(String(64), nullable=False, index=True)
    category = Column(String(80), nullable=False)
    department = Column(String(120), nullable=False)
    priority = Column(String(20), nullable=False)
    summary = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    source = Column(String(30), nullable=False)  # 'groq' or 'fallback'
    model = Column(String(80), nullable=False)
    raw_json = Column(Text, nullable=True)
    final_category = Column(String(80), nullable=True)
    final_priority = Column(String(20), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    grievance = relationship("Grievance", back_populates="ai_analyses")

