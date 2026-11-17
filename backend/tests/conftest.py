import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db
from app.models import User, Department, Grievance, GrievanceHistory
from app.security import get_password_hash, create_access_token

# Use in-memory SQLite database for test suite
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh tables for every test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed base departments
    pwd_dept = Department(name="Public Works", description="Roads and Bridges", is_featured=True)
    health_dept = Department(name="Health and Family Welfare", description="Hospitals and Clinics", is_featured=True)
    water_dept = Department(name="Water Resources", description="Water Supply", is_featured=True)
    session.add_all([pwd_dept, health_dept, water_dept])
    session.flush()

    # Seed test users
    pw = get_password_hash("TestPass123")
    cmo = User(name="Test CMO", email="cmo@test.com", mobile="9847000001", password_hash=pw, role="cmo_admin", is_active=True)
    off_pwd = User(name="PWD Officer", email="officer.pwd@test.com", mobile="9847000002", password_hash=pw, role="officer", department_id=pwd_dept.id, is_active=True)
    off_health = User(name="Health Officer", email="officer.health@test.com", mobile="9847000003", password_hash=pw, role="officer", department_id=health_dept.id, is_active=True)
    cit_a = User(name="Citizen A", email="citizen.a@test.com", mobile="9847000004", password_hash=pw, role="citizen", is_active=True)
    cit_b = User(name="Citizen B", email="citizen.b@test.com", mobile="9847000005", password_hash=pw, role="citizen", is_active=True)

    session.add_all([cmo, off_pwd, off_health, cit_a, cit_b])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with db override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    def _make_headers(user: User):
        token = create_access_token({
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "name": user.name,
        })
        return {"Authorization": f"Bearer {token}"}
    return _make_headers
