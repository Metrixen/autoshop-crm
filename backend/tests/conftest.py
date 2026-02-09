"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Shop, Staff, Customer, UserRole
from app.utils.auth import get_password_hash

# Test database URL (in-memory SQLite for isolation)
TEST_DATABASE_URL = "sqlite:///./test_autoshop.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_shop(db):
    """Create a test shop"""
    shop = Shop(
        name="Test Auto Shop",
        address="Test Address",
        phone="+1234567890",
        email="test@shop.com",
        labor_rate_per_hour=50.0,
        is_active=True
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


@pytest.fixture
def test_staff(db, test_shop):
    """Create a test staff member"""
    staff = Staff(
        shop_id=test_shop.id,
        username="teststaff",
        email="staff@test.com",
        phone="+1234567891",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="Staff",
        role=UserRole.RECEPTIONIST,
        is_active=True
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@pytest.fixture
def test_customer(db, test_shop):
    """Create a test customer"""
    customer = Customer(
        shop_id=test_shop.id,
        phone="+1234567892",
        email="customer@test.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="Customer",
        is_active=True
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def inactive_staff(db, test_shop):
    """Create an inactive test staff member"""
    staff = Staff(
        shop_id=test_shop.id,
        username="inactivestaff",
        email="inactive@test.com",
        phone="+1234567893",
        password_hash=get_password_hash("testpass123"),
        first_name="Inactive",
        last_name="Staff",
        role=UserRole.MECHANIC,
        is_active=False
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff
