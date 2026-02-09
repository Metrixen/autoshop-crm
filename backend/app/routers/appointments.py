from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Appointment, AppointmentStatus, Staff, Customer, Car, WorkOrder, UserRole
from app.schemas import (Appointment as AppointmentSchema, AppointmentCreate, AppointmentUpdate, 
                          AppointmentWithDetails, WorkOrderCreate)
from app.utils.auth import get_current_staff, get_receptionist_or_higher, get_current_customer, get_current_user
from app.services.sms import get_sms_service, SMSService
from app.config import settings

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentSchema, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Customer books an appointment"""
    
    # Verify customer is booking for themselves
    if appointment_data.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="Can only book appointments for yourself")
    
    # If car_id provided, verify it belongs to the customer
    if appointment_data.car_id:
        car = db.query(Car).filter(
            Car.id == appointment_data.car_id,
            Car.owner_id == current_customer.id
        ).first()
        
        if not car:
            raise HTTPException(status_code=404, detail="Car not found or doesn't belong to you")
    
    appointment = Appointment(**appointment_data.dict())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.get("", response_model=List[AppointmentWithDetails])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    status_filter: AppointmentStatus = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List appointments"""
    
    if isinstance(current_user, Staff):
        query = db.query(Appointment).filter(Appointment.shop_id == current_user.shop_id)
    elif isinstance(current_user, Customer):
        query = db.query(Appointment).filter(
            Appointment.shop_id == current_user.shop_id,
            Appointment.customer_id == current_user.id
        )
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(Appointment.preferred_date.desc()).offset(skip).limit(limit).all()
    return appointments


@router.get("/pending", response_model=List[AppointmentWithDetails])
def get_pending_appointments(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Get pending appointment requests"""
    
    appointments = db.query(Appointment).filter(
        Appointment.shop_id == current_staff.shop_id,
        Appointment.status == AppointmentStatus.REQUESTED
    ).order_by(Appointment.preferred_date).all()
    
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentWithDetails)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get appointment by ID"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization
    if isinstance(current_user, Staff):
        if appointment.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif isinstance(current_user, Customer):
        if appointment.customer_id != current_user.id or appointment.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Update appointment (confirm, reject, or mark as arrived)"""
    
    sms_service = get_sms_service(db)
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.shop_id == current_staff.shop_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    old_status = appointment.status
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(appointment, field, value)
    
    # Handle status changes
    if update_data.status == AppointmentStatus.CONFIRMED and old_status == AppointmentStatus.REQUESTED:
        appointment.confirmed_by_staff_id = current_staff.id
        
        # Send confirmation SMS
        customer = db.query(Customer).filter(Customer.id == appointment.customer_id).first()
        if customer and not appointment.sms_sent:
            customer_name = f"{customer.first_name} {customer.last_name}"
            confirmed_date = update_data.confirmed_date or appointment.preferred_date
            
            sms_service.send_appointment_confirmed_sms(
                shop_id=appointment.shop_id,
                customer_phone=customer.phone,
                customer_name=customer_name,
                date=confirmed_date,
                shop_website=settings.SHOP_WEBSITE
            )
            
            appointment.sms_sent = True
            appointment.sms_sent_at = datetime.utcnow()
    
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/convert-to-work-order", response_model=dict)
def convert_appointment_to_work_order(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Convert appointment to work order when customer arrives"""
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.shop_id == current_staff.shop_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status != AppointmentStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Appointment must be confirmed first")
    
    # Check if work order already exists for this appointment
    existing_wo = db.query(WorkOrder).filter(WorkOrder.appointment_id == appointment.id).first()
    if existing_wo:
        return {"message": "Work order already exists", "work_order_id": existing_wo.id}
    
    # Create work order
    if not appointment.car_id:
        raise HTTPException(status_code=400, detail="Cannot create work order for unregistered car")
    
    work_order = WorkOrder(
        shop_id=appointment.shop_id,
        customer_id=appointment.customer_id,
        car_id=appointment.car_id,
        appointment_id=appointment.id,
        reported_issues=appointment.issue_description,
        status="created"
    )
    
    db.add(work_order)
    
    # Update appointment status
    appointment.status = AppointmentStatus.ARRIVED
    appointment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(work_order)
    
    return {"message": "Work order created successfully", "work_order_id": work_order.id}


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel appointment"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization - customers can cancel their own, staff can cancel any in their shop
    if isinstance(current_user, Customer):
        if appointment.customer_id != current_user.id or appointment.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif isinstance(current_user, Staff):
        if appointment.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Don't allow canceling if already arrived
    if appointment.status == AppointmentStatus.ARRIVED:
        raise HTTPException(status_code=400, detail="Cannot cancel appointment that has already arrived")
    
    db.delete(appointment)
    db.commit()
    return None
