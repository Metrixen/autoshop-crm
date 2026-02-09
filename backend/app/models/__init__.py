from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    MECHANIC = "mechanic"
    CUSTOMER = "customer"


class WorkOrderStatus(str, enum.Enum):
    """Work order status flow"""
    CREATED = "created"
    DIAGNOSING = "diagnosing"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class InvoiceStatus(str, enum.Enum):
    """Invoice status flow"""
    DRAFT = "draft"
    FINALIZED = "finalized"
    PAID = "paid"


class AppointmentStatus(str, enum.Enum):
    """Appointment status flow"""
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ARRIVED = "arrived"
    REJECTED = "rejected"


class Shop(Base):
    """Shop/Tenant entity - each shop is a separate deployment"""
    __tablename__ = "shops"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    logo_url = Column(String(500))
    
    # Configuration
    working_hours = Column(String(500))  # JSON string
    number_of_bays = Column(Integer, default=2)
    labor_rate_per_hour = Column(Float, default=50.0)
    data_retention_days = Column(Integer, default=365)
    
    # Feature flags
    online_payments_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)
    mechanics_see_pricing = Column(Boolean, default=True)
    
    # Billing
    subscription_plan = Column(String(50), default="basic")
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    trial_ends_at = Column(DateTime)
    sms_usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    staff = relationship("Staff", back_populates="shop")
    customers = relationship("Customer", back_populates="shop")
    cars = relationship("Car", back_populates="shop")
    work_orders = relationship("WorkOrder", back_populates="shop")
    invoices = relationship("Invoice", back_populates="shop")
    appointments = relationship("Appointment", back_populates="shop")


class Staff(Base):
    """Staff members (managers, receptionists, mechanics)"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    specialty = Column(String(255))  # For mechanics
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="staff")
    assigned_work_orders = relationship("WorkOrder", back_populates="assigned_mechanic")


class Customer(Base):
    """Customer entity"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    phone = Column(String(20), nullable=False, index=True)  # Unique per shop, used for login
    email = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # GDPR
    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_date = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="customers")
    cars = relationship("Car", back_populates="owner")
    appointments = relationship("Appointment", back_populates="customer")
    work_orders = relationship("WorkOrder", back_populates="customer")


class Car(Base):
    """Car entity"""
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    vin = Column(String(17))
    license_plate = Column(String(20), nullable=False, index=True)
    
    color = Column(String(50))
    current_mileage = Column(Integer, default=0)
    service_interval_km = Column(Integer, default=10000)
    
    photos = Column(Text)  # JSON array of photo URLs
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="cars")
    owner = relationship("Customer", back_populates="cars")
    work_orders = relationship("WorkOrder", back_populates="car")
    appointments = relationship("Appointment", back_populates="car")
    ownership_history = relationship("CarOwnershipHistory", back_populates="car")


class CarOwnershipHistory(Base):
    """Track car ownership transfers"""
    __tablename__ = "car_ownership_history"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    previous_owner_id = Column(Integer, ForeignKey("customers.id"))
    new_owner_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    transferred_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    
    transfer_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    car = relationship("Car", back_populates="ownership_history")


class Appointment(Base):
    """Customer appointment requests"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"))  # Null for unregistered cars
    
    # For unregistered cars
    unregistered_car_details = Column(Text)
    
    issue_description = Column(Text, nullable=False)
    preferred_date = Column(DateTime, nullable=False)
    preferred_time = Column(String(50))
    
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.REQUESTED)
    
    confirmed_date = Column(DateTime)
    confirmed_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    rejection_reason = Column(Text)
    
    # SMS tracking
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    car = relationship("Car", back_populates="appointments")


class WorkOrder(Base):
    """Work order entity"""
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    assigned_mechanic_id = Column(Integer, ForeignKey("staff.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"))  # If created from appointment
    
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.CREATED)
    
    # Intake information
    reported_issues = Column(Text, nullable=False)
    mileage_at_intake = Column(Integer)
    
    # Mechanic work
    diagnostic_notes = Column(Text)
    mechanic_notes = Column(Text)
    
    # Photos
    photos_before = Column(Text)  # JSON array
    photos_after = Column(Text)  # JSON array
    
    # Time tracking
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="work_orders")
    customer = relationship("Customer", back_populates="work_orders")
    car = relationship("Car", back_populates="work_orders")
    assigned_mechanic = relationship("Staff", back_populates="assigned_work_orders")
    line_items = relationship("WorkOrderLineItem", back_populates="work_order", cascade="all, delete-orphan")
    assignment_history = relationship("WorkOrderAssignmentHistory", back_populates="work_order")
    invoice = relationship("Invoice", back_populates="work_order", uselist=False)


class WorkOrderLineItem(Base):
    """Line items for work orders (parts and labor)"""
    __tablename__ = "work_order_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    
    item_type = Column(String(20), nullable=False)  # 'part' or 'labor'
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    notes = Column(Text)
    
    added_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="line_items")


class WorkOrderAssignmentHistory(Base):
    """Track work order reassignments"""
    __tablename__ = "work_order_assignment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    previous_mechanic_id = Column(Integer, ForeignKey("staff.id"))
    new_mechanic_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    reassigned_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    
    reason = Column(Text)
    reassigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="assignment_history")


class Invoice(Base):
    """Invoice entity"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    
    notes = Column(Text)
    
    # Payment
    payment_method = Column(String(50))  # 'cash', 'card', 'online', etc.
    paid_at = Column(DateTime)
    stripe_payment_intent_id = Column(String(255))
    
    # PDF
    pdf_url = Column(String(500))
    
    finalized_at = Column(DateTime)
    finalized_by_staff_id = Column(Integer, ForeignKey("staff.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="invoices")
    work_order = relationship("WorkOrder", back_populates="invoice")
    customer = relationship("Customer")


class SMSLog(Base):
    """Track SMS messages sent"""
    __tablename__ = "sms_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    recipient_phone = Column(String(20), nullable=False)
    message_type = Column(String(50), nullable=False)  # 'welcome', 'appointment_confirmed', etc.
    message_body = Column(Text, nullable=False)
    
    twilio_sid = Column(String(100))
    status = Column(String(50))  # 'sent', 'delivered', 'failed'
    error_message = Column(Text)
    
    sent_at = Column(DateTime, default=datetime.utcnow)


class ServiceReminder(Base):
    """Track service reminders sent"""
    __tablename__ = "service_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    predicted_mileage = Column(Integer, nullable=False)
    service_due_mileage = Column(Integer, nullable=False)
    
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
