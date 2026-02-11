from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, WorkOrderStatus, InvoiceStatus, AppointmentStatus


# ===== Authentication Schemas =====

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
    shop_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str  # Phone for customers, username/email for staff
    password: str


# ===== Shop Schemas =====

class ShopBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None


class ShopCreate(ShopBase):
    labor_rate_per_hour: float = 50.0
    online_payments_enabled: bool = False
    sms_enabled: bool = False


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    number_of_bays: Optional[int] = None
    labor_rate_per_hour: Optional[float] = None
    mechanics_see_pricing: Optional[bool] = None
    online_payments_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None


class Shop(ShopBase):
    id: int
    working_hours: Optional[str]
    number_of_bays: int
    labor_rate_per_hour: float
    online_payments_enabled: bool
    sms_enabled: bool
    mechanics_see_pricing: bool
    is_active: bool
    subscription_plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Staff Schemas =====

class StaffBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    role: UserRole
    specialty: Optional[str] = None


class StaffCreate(StaffBase):
    password: str
    shop_id: int


class StaffUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None


class Staff(StaffBase):
    id: int
    shop_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Customer Schemas =====

class CustomerBase(BaseModel):
    phone: str
    email: Optional[EmailStr] = None
    first_name: str
    last_name: str


class CustomerCreate(CustomerBase):
    shop_id: int
    password: Optional[str] = None  # Auto-generated if not provided


class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gdpr_consent: Optional[bool] = None


class CustomerPasswordChange(BaseModel):
    current_password: str
    new_password: str


class Customer(CustomerBase):
    id: int
    shop_id: int
    gdpr_consent: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Car Schemas =====

class CarBase(BaseModel):
    make: str
    model: str
    year: Optional[int] = None
    vin: Optional[str] = None
    license_plate: str
    color: Optional[str] = None
    service_interval_km: int = 10000


class CarCreate(CarBase):
    owner_id: int
    shop_id: int
    current_mileage: int = 0


class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    color: Optional[str] = None
    current_mileage: Optional[int] = None
    service_interval_km: Optional[int] = None
    notes: Optional[str] = None


class CarOwnershipTransfer(BaseModel):
    new_owner_id: int
    notes: Optional[str] = None


class Car(CarBase):
    id: int
    shop_id: int
    owner_id: int
    current_mileage: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CarWithOwner(Car):
    owner: Customer


# ===== Appointment Schemas =====

class AppointmentBase(BaseModel):
    issue_description: str
    preferred_date: datetime
    preferred_time: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    customer_id: int
    shop_id: int
    car_id: Optional[int] = None
    unregistered_car_details: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    confirmed_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class Appointment(AppointmentBase):
    id: int
    shop_id: int
    customer_id: int
    car_id: Optional[int]
    unregistered_car_details: Optional[str]
    status: AppointmentStatus
    confirmed_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentWithDetails(Appointment):
    customer: Customer
    car: Optional[Car]


# ===== Work Order Schemas =====

class WorkOrderLineItemBase(BaseModel):
    item_type: str  # 'part' or 'labor'
    description: str
    quantity: float = 1.0
    unit_price: float


class WorkOrderLineItemCreate(WorkOrderLineItemBase):
    pass


class WorkOrderLineItem(WorkOrderLineItemBase):
    id: int
    work_order_id: int
    total_price: float
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkOrderBase(BaseModel):
    reported_issues: str
    mileage_at_intake: Optional[int] = None


class WorkOrderCreate(WorkOrderBase):
    customer_id: int
    car_id: int
    shop_id: int
    assigned_mechanic_id: Optional[int] = None
    appointment_id: Optional[int] = None


class WorkOrderUpdate(BaseModel):
    status: Optional[WorkOrderStatus] = None
    assigned_mechanic_id: Optional[int] = None
    diagnostic_notes: Optional[str] = None
    mechanic_notes: Optional[str] = None
    mileage_at_intake: Optional[int] = None


class WorkOrderReassign(BaseModel):
    new_mechanic_id: int
    reason: Optional[str] = None


class WorkOrder(WorkOrderBase):
    id: int
    shop_id: int
    customer_id: int
    car_id: int
    assigned_mechanic_id: Optional[int]
    status: WorkOrderStatus
    diagnostic_notes: Optional[str]
    mechanic_notes: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkOrderWithDetails(WorkOrder):
    customer: Customer
    car: Car
    assigned_mechanic: Optional[Staff]
    line_items: List[WorkOrderLineItem] = []


# ===== Invoice Schemas =====

class InvoiceBase(BaseModel):
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    work_order_id: int
    shop_id: int
    customer_id: int


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None


class Invoice(InvoiceBase):
    id: int
    shop_id: int
    work_order_id: int
    customer_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    payment_method: Optional[str]
    paid_at: Optional[datetime]
    pdf_url: Optional[str]
    finalized_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceWithDetails(Invoice):
    work_order: WorkOrder
    customer: Customer


# ===== Analytics/Reports Schemas =====

class DashboardStats(BaseModel):
    total_customers: int
    active_work_orders: int
    completed_work_orders_today: int
    revenue_today: float
    revenue_week: float
    revenue_month: float
    pending_appointments: int


class MechanicPerformance(BaseModel):
    mechanic_id: int
    mechanic_name: str
    completed_work_orders: int
    average_completion_time_hours: float
    total_revenue: float


class RevenueBreakdown(BaseModel):
    date: str
    revenue: float
    work_orders_count: int


class PopularService(BaseModel):
    service_name: str
    count: int
    total_revenue: float


# ===== Service Reminder Schemas =====

class ServiceReminderCreate(BaseModel):
    car_id: int
    customer_id: int
    predicted_mileage: int
    service_due_mileage: int


class ServiceReminder(BaseModel):
    id: int
    car_id: int
    customer_id: int
    predicted_mileage: int
    service_due_mileage: int
    reminder_sent: bool
    reminder_sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Car Service History Schemas =====

class CarOwnershipHistorySchema(BaseModel):
    id: int
    car_id: int
    previous_owner_id: Optional[int]
    new_owner_id: int
    transfer_date: datetime
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class CarServiceHistory(BaseModel):
    car: Car
    work_orders: List[WorkOrder] = []
    ownership_history: List[CarOwnershipHistorySchema] = []


# ===== SMS Log Schemas =====

class SMSLog(BaseModel):
    id: int
    shop_id: int
    recipient_phone: str
    message_type: str
    message_body: str
    twilio_sid: Optional[str]
    status: Optional[str]
    error_message: Optional[str]
    sent_at: datetime
    
    class Config:
        from_attributes = True
