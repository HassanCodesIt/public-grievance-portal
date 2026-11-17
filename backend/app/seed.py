import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .db import SessionLocal, engine, Base
from .models import (
    User,
    Department,
    Grievance,
    GrievanceHistory,
    DepartmentAssignment,
    Attachment,
    ActionReport,
    CitizenFeedback,
    AiAnalysis,
)
from .security import get_password_hash
from .services.workflow import calculate_due_date, generate_reference_no

DEPARTMENTS_DATA = [
    {"name": "Public Works", "description": "Roads, bridges and public infrastructure.", "is_featured": True},
    {"name": "Health and Family Welfare", "description": "Public health facilities and services.", "is_featured": True},
    {"name": "General Education", "description": "Schools and educational administration.", "is_featured": True},
    {"name": "Water Resources", "description": "Water supply, irrigation and conservation.", "is_featured": True},
    {"name": "Electricity", "description": "Power supply and electrical infrastructure.", "is_featured": True},
    {"name": "Local Self Government", "description": "Municipal and panchayat public services.", "is_featured": True},
    {"name": "Civil Supplies", "description": "Ration cards and public distribution.", "is_featured": True},
    {"name": "Revenue", "description": "Land records, certificates and revenue matters.", "is_featured": True},
    {"name": "Transport", "description": "Public transport and road safety.", "is_featured": True},
    {"name": "Social Justice", "description": "Inclusive welfare and social support.", "is_featured": True},
]

# Minimal valid 1x1 PNG image for demo attachments
DUMMY_PNG_DATA = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00"
    b"\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def seed_database():
    """Seed the database with departments, demo users, and 25+ fictional grievances."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Departments
        dept_map = {}
        for d in DEPARTMENTS_DATA:
            existing = db.query(Department).filter(Department.name == d["name"]).first()
            if not existing:
                existing = Department(
                    name=d["name"],
                    description=d["description"],
                    is_featured=d["is_featured"],
                )
                db.add(existing)
                db.flush()
            dept_map[existing.name] = existing

        # 2. Seed Users
        demo_password_hash = get_password_hash("Demo@123")

        users_to_seed = [
            # Plan.md official demo accounts
            {"name": "Ananya Menon", "email": "cmo.admin@example.test", "mobile": "9847012345", "role": "cmo_admin", "dept": None},
            {"name": "Ravi Kumar", "email": "officer.pwd@example.test", "mobile": "9847012346", "role": "officer", "dept": dept_map["Public Works"].id},
            {"name": "Dr. Lakshmi Nair", "email": "officer.health@example.test", "mobile": "9847012347", "role": "officer", "dept": dept_map["Health and Family Welfare"].id},
            {"name": "Meera Krishnan", "email": "citizen.demo@example.test", "mobile": "9847012348", "role": "citizen", "dept": None},
            # Frontend quick-login accounts
            {"name": "Ananya Menon", "email": "admin@janasevanam.example.test", "mobile": "9847012341", "role": "cmo_admin", "dept": None},
            {"name": "Ravi Kumar", "email": "officer@janasevanam.example.test", "mobile": "9847012342", "role": "officer", "dept": dept_map["Public Works"].id},
            {"name": "Meera Krishnan", "email": "citizen@janasevanam.example.test", "mobile": "9847012343", "role": "citizen", "dept": None},
            # Additional citizen accounts
            {"name": "Arun Das", "email": "arun.das@example.test", "mobile": "9847055551", "role": "citizen", "dept": None},
            {"name": "Nila Thomas", "email": "nila.thomas@example.test", "mobile": "9847055552", "role": "citizen", "dept": None},
            {"name": "Devika Raj", "email": "devika.raj@example.test", "mobile": "9847055553", "role": "citizen", "dept": None},
            {"name": "Fahad Ali", "email": "fahad.ali@example.test", "mobile": "9847055554", "role": "citizen", "dept": None},
        ]

        user_map = {}
        for u in users_to_seed:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if not existing_user:
                existing_user = User(
                    name=u["name"],
                    email=u["email"],
                    mobile=u["mobile"],
                    password_hash=demo_password_hash,
                    role=u["role"],
                    department_id=u["dept"],
                    is_active=True,
                )
                db.add(existing_user)
                db.flush()
            user_map[u["email"]] = existing_user

        cmo_user = user_map["cmo.admin@example.test"]
        pwd_officer = user_map["officer.pwd@example.test"]
        health_officer = user_map["officer.health@example.test"]
        citizen_meera = user_map["citizen.demo@example.test"]

        # 3. Check if grievances already seeded
        existing_count = db.query(Grievance).count()
        if existing_count >= 20:
            print(f"Database already contains {existing_count} grievances. Seed skipped.")
            db.commit()
            return

        # 4. 25+ Fictional Grievances
        RAW_GRIEVANCES = [
            ("Damaged road near the market junction with severe potholes", "Roads and Infrastructure", "Public Works", "Ernakulam", "High", "In Progress", False, 18),
            ("Primary health centre without evening medical doctor coverage", "Healthcare", "Health and Family Welfare", "Wayanad", "High", "In Progress", True, 16),
            ("Irregular drinking water supply for two weeks in ward 4", "Water Supply", "Water Resources", "Kozhikode", "High", "Resolved", False, 20),
            ("Streetlights not working on the school bypass road", "Electricity", "Electricity", "Thrissur", "Medium", "Submitted", False, 3),
            ("Delay in updating ration card family member details", "Public Distribution", "Civil Supplies", "Kollam", "Low", "Under Review", False, 12),
            ("Unsafe pedestrian crossing near government arts college", "Transport", "Transport", "Kottayam", "High", "Reopened", False, 15),
            ("Waste collection missed for several days causing foul smell", "Waste and Sanitation", "Local Self Government", "Alappuzha", "Medium", "In Progress", False, 10),
            ("School classroom roof leaks during heavy monsoon showers", "Education", "General Education", "Palakkad", "High", "Resolved", False, 25),
            ("Delay in updating land tax records after partition deed", "Land and Revenue", "Revenue", "Idukki", "Low", "Under Review", False, 8),
            ("Accessible wheelchair ramp needed at community panchayat hall", "Other", "Social Justice", "Kannur", "Low", "Submitted", False, 2),
            ("Low water pressure in hillside ward residential sector", "Water Supply", "Water Resources", "Malappuram", "Medium", "In Progress", False, 9),
            ("Deep potholes on the main KSRTC bus route", "Roads and Infrastructure", "Public Works", "Kasaragod", "High", "Resolved", False, 30),
            ("Broken culvert causing flash flooding across town lane", "Roads and Infrastructure", "Public Works", "Thiruvananthapuram", "High", "Under Review", False, 7),
            ("Shortage of essential rabies vaccines at taluk hospital", "Healthcare", "Health and Family Welfare", "Pathanamthitta", "High", "In Progress", True, 14),
            ("Overhanging electric cables near primary school gate", "Electricity", "Electricity", "Kozhikode", "High", "Submitted", False, 1),
            ("Drainage blockage leading to wastewater overflow on market road", "Waste and Sanitation", "Local Self Government", "Ernakulam", "Medium", "Resolved", False, 18),
            ("Delay in issuing legal heir certificate for pension transfer", "Land and Revenue", "Revenue", "Thrissur", "Low", "Submitted", False, 4),
            ("Overcrowded morning school bus service on rural route", "Transport", "Transport", "Palakkad", "Medium", "In Progress", False, 11),
            ("Non-functional borewell pump in drought-prone tribal hamlet", "Water Supply", "Water Resources", "Wayanad", "High", "In Progress", True, 17),
            ("Cracked retaining wall along river bank road", "Roads and Infrastructure", "Public Works", "Alappuzha", "High", "Under Review", False, 5),
            ("Bio-waste treatment plant emitting untreated foul emissions", "Waste and Sanitation", "Local Self Government", "Kollam", "Medium", "Resolved", False, 22),
            ("Old transformer sparking repeatedly during rain showers", "Electricity", "Electricity", "Malappuram", "High", "In Progress", False, 6),
            ("Inaccessible public footbridge for senior citizens and disabled", "Other", "Social Justice", "Kottayam", "Low", "Resolved", False, 28),
            ("Ration shop denying subsidised wheat quota to eligible cardholders", "Public Distribution", "Civil Supplies", "Kannur", "Medium", "Submitted", False, 2),
            ("Sub-centre building requires painting and structural repairs", "Healthcare", "Health and Family Welfare", "Kasaragod", "Low", "Under Review", False, 9),
            ("School sports ground waterlogged due to blocked public canal", "Education", "General Education", "Idukki", "Medium", "Reopened", False, 19),
        ]

        now = datetime.utcnow()

        for idx, (subj, cat, dept_name, dist, prio, stat, esc, age_days) in enumerate(RAW_GRIEVANCES, start=1):
            created_at = now - timedelta(days=age_days)
            updated_at = now - timedelta(days=max(0, age_days - 3))
            
            # Make a few items specifically overdue
            if idx in (1, 2, 7, 14, 19):
                due_at = now - timedelta(days=2)  # Overdue!
            else:
                due_at = calculate_due_date(prio, created_at)

            # Assign citizen
            if idx <= 6:
                citizen = citizen_meera
            else:
                citizen_emails = ["arun.das@example.test", "nila.thomas@example.test", "devika.raj@example.test", "fahad.ali@example.test"]
                citizen = user_map[citizen_emails[idx % 4]]

            dept = dept_map.get(dept_name)

            grievance = Grievance(
                citizen_id=citizen.id,
                district=dist,
                category=cat,
                subject=subj,
                description=f"{subj}. Local residents and commuters are facing severe difficulties. We request immediate inspection and redressal.",
                priority=prio,
                status=stat,
                due_at=due_at,
                escalated=esc,
                department_id=dept.id if dept else None,
                ai_summary=f"Citizen from {dist} reports {subj.lower()}. Requires prompt inspection and update by {dept_name}.",
                created_at=created_at,
                updated_at=updated_at,
            )
            db.add(grievance)
            db.flush()

            grievance.reference_no = f"CMK-2026-{idx:06d}"

            # Add AI Analysis row
            input_hash = hashlib.sha256(grievance.description.lower().encode("utf-8")).hexdigest()
            ai_row = AiAnalysis(
                grievance_id=grievance.id,
                input_hash=input_hash,
                category=cat,
                department=dept_name,
                priority=prio,
                summary=grievance.ai_summary,
                confidence=0.88,
                reasoning=f"Identified clear departmental keywords for {cat}.",
                source="groq",
                model="openai/gpt-oss-120b",
                final_category=cat,
                final_priority=prio,
                reviewed_by=cmo_user.id if stat != "Submitted" else None,
                created_at=created_at,
            )
            db.add(ai_row)

            # History trail
            h1 = GrievanceHistory(
                grievance_id=grievance.id,
                from_status=None,
                to_status="Submitted",
                remark="Grievance submitted and reference number generated.",
                visibility="Public",
                actor_id=citizen.id,
                actor_name=citizen.name,
                actor_role="Citizen",
                created_at=created_at,
            )
            db.add(h1)

            if stat in ("Under Review", "In Progress", "Resolved", "Reopened"):
                h2 = GrievanceHistory(
                    grievance_id=grievance.id,
                    from_status="Submitted",
                    to_status="Under Review",
                    remark="Grievance reviewed by CMO and category/priority confirmed.",
                    visibility="Public",
                    actor_id=cmo_user.id,
                    actor_name=cmo_user.name,
                    actor_role="CMO Reviewer",
                    created_at=created_at + timedelta(days=1),
                )
                db.add(h2)

            if stat in ("In Progress", "Resolved", "Reopened"):
                assign_officer = pwd_officer if dept_name == "Public Works" else health_officer if dept_name == "Health and Family Welfare" else None
                assignment = DepartmentAssignment(
                    grievance_id=grievance.id,
                    department_id=dept.id,
                    officer_id=assign_officer.id if assign_officer else None,
                    assigned_by=cmo_user.id,
                    state="Closed" if stat == "Resolved" else "Assigned",
                    assigned_at=created_at + timedelta(days=2),
                )
                db.add(assignment)
                db.flush()

                h3 = GrievanceHistory(
                    grievance_id=grievance.id,
                    from_status="Under Review",
                    to_status="In Progress",
                    remark=f"Forwarded to {dept_name} for departmental field action.",
                    visibility="Public",
                    actor_id=cmo_user.id,
                    actor_name=cmo_user.name,
                    actor_role="CMO Reviewer",
                    created_at=created_at + timedelta(days=2),
                )
                db.add(h3)

                if stat in ("Resolved", "Reopened"):
                    # Add Action Report
                    report = ActionReport(
                        assignment_id=assignment.id,
                        text=f"Field inspection completed for {subj}. Remedial maintenance executed and service functionality verified.",
                        submitted_by=assign_officer.id if assign_officer else cmo_user.id,
                        submitted_at=created_at + timedelta(days=5),
                        cmo_decision="accept",
                        cmo_remark="Action report verified and verified on site.",
                        decided_at=created_at + timedelta(days=6),
                    )
                    db.add(report)

                    h4 = GrievanceHistory(
                        grievance_id=grievance.id,
                        from_status="In Progress",
                        to_status="Resolved",
                        remark="Department action report reviewed and confirmed. Grievance resolved.",
                        visibility="Public",
                        actor_id=cmo_user.id,
                        actor_name=cmo_user.name,
                        actor_role="CMO Reviewer",
                        created_at=created_at + timedelta(days=6),
                    )
                    db.add(h4)

                if stat == "Reopened":
                    h5 = GrievanceHistory(
                        grievance_id=grievance.id,
                        from_status="Resolved",
                        to_status="Reopened",
                        remark="The reported problem recurred after heavy rain. Requesting further inspection.",
                        visibility="Public",
                        actor_id=citizen.id,
                        actor_name=citizen.name,
                        actor_role="Citizen",
                        created_at=updated_at,
                    )
                    db.add(h5)

            if esc:
                h_esc = GrievanceHistory(
                    grievance_id=grievance.id,
                    from_status=grievance.status,
                    to_status=grievance.status,
                    remark="Grievance escalated by CMO for immediate departmental intervention.",
                    visibility="Internal",
                    actor_id=cmo_user.id,
                    actor_name=cmo_user.name,
                    actor_role="CMO Reviewer",
                    created_at=now - timedelta(days=1),
                )
                db.add(h_esc)

            # Seed feedback on item #3
            if idx == 3 and stat == "Resolved":
                fb = CitizenFeedback(
                    grievance_id=grievance.id,
                    rating=5,
                    comment="Quick resolution after CMO intervention. Thank you!",
                    created_at=updated_at,
                )
                db.add(fb)

            # Seed sample attachment on item #1
            if idx == 1:
                att = Attachment(
                    grievance_id=grievance.id,
                    uploaded_by=citizen.id,
                    kind="grievance",
                    filename="market_road_damage.png",
                    content_type="image/png",
                    size=len(DUMMY_PNG_DATA),
                    data=DUMMY_PNG_DATA,
                    created_at=created_at,
                )
                db.add(att)

        db.commit()
        print("Successfully seeded departments, demo users, and 26 fictional grievances.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

