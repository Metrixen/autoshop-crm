from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Customer, Staff, UserRole
from app.schemas import Customer as CustomerSchema, CustomerCreate, CustomerUpdate, CustomerPasswordChange
from app.utils.auth import get_current_staff, get_receptionist_or_higher, get_current_customer, get_password_hash, verify_password
from app.utils.helpers import generate_password, validate_phone_number
from app.services.sms import get_sms_service, SMSService
from app.config import settings

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.post("", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
def register_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Register a new customer (receptionist or higher)"""
    
    sms_service = get_sms_service(db)
    
    # Validate phone number
    formatted_phone = validate_phone_number(customer_data.phone)
    if not formatted_phone:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    # Check if customer with this phone already exists in the shop
    existing = db.query(Customer).filter(
        Customer.phone == formatted_phone,
        Customer.shop_id == customer_data.shop_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
    
    # Generate password if not provided
    password = customer_data.password or generate_password()
    
    # Create customer
    customer = Customer(
        shop_id=customer_data.shop_id,
        phone=formatted_phone,
        email=customer_data.email,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        password_hash=get_password_hash(password)
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # Send welcome SMS with password
    customer_name = f"{customer.first_name} {customer.last_name}"
    sms_service.send_welcome_sms(
        shop_id=customer.shop_id,
        customer_phone=customer.phone,
        customer_name=customer_name,
        password=password,
        shop_website=settings.SHOP_WEBSITE
    )
    
    return customer


@router.get("", response_model=List[CustomerSchema])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """List all customers in the shop"""
    query = db.query(Customer).filter(Customer.shop_id == current_staff.shop_id)
    
    if search:
        query = query.filter(
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )
    
    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/me", response_model=CustomerSchema)
def get_current_customer_profile(current_customer: Customer = Depends(get_current_customer)):
    """Get current customer's profile"""
    return current_customer


@router.get("/{customer_id}", response_model=CustomerSchema)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get customer by ID"""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.shop_id == current_staff.shop_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


@router.put("/me", response_model=CustomerSchema)
def update_customer_profile(
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Update current customer's profile"""
    
    if update_data.email is not None:
        current_customer.email = update_data.email
    if update_data.first_name is not None:
        current_customer.first_name = update_data.first_name
    if update_data.last_name is not None:
        current_customer.last_name = update_data.last_name
    if update_data.gdpr_consent is not None:
        current_customer.gdpr_consent = update_data.gdpr_consent
        if update_data.gdpr_consent and not current_customer.gdpr_consent_date:
            from datetime import datetime
            current_customer.gdpr_consent_date = datetime.utcnow()
    
    db.commit()
    db.refresh(current_customer)
    return current_customer


@router.put("/{customer_id}", response_model=CustomerSchema)
def update_customer(
    customer_id: int,
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Update customer by ID (receptionist or higher)"""
    
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.shop_id == current_staff.shop_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if update_data.email is not None:
        customer.email = update_data.email
    if update_data.first_name is not None:
        customer.first_name = update_data.first_name
    if update_data.last_name is not None:
        customer.last_name = update_data.last_name
    
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/me/change-password")
def change_password(
    password_data: CustomerPasswordChange,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Change customer password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_customer.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Update password
    current_customer.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Deactivate customer (soft delete)"""
    
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.shop_id == current_staff.shop_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_active = False
    db.commit()
    return None
