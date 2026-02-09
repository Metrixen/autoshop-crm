from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Car, Customer, Staff, CarOwnershipHistory
from app.schemas import Car as CarSchema, CarCreate, CarUpdate, CarOwnershipTransfer, CarWithOwner
from app.utils.auth import get_current_staff, get_receptionist_or_higher, get_current_customer

router = APIRouter(prefix="/api/cars", tags=["Cars"])


@router.post("/", response_model=CarSchema, status_code=status.HTTP_201_CREATED)
def create_car(
    car_data: CarCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Create a new car (receptionist or higher)"""
    
    # Verify owner exists and belongs to the same shop
    owner = db.query(Customer).filter(
        Customer.id == car_data.owner_id,
        Customer.shop_id == car_data.shop_id
    ).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if license plate already exists in shop
    existing = db.query(Car).filter(
        Car.license_plate == car_data.license_plate,
        Car.shop_id == car_data.shop_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Car with this license plate already exists")
    
    car = Car(**car_data.dict())
    db.add(car)
    db.commit()
    db.refresh(car)
    
    return car


@router.get("/", response_model=List[CarWithOwner])
def list_cars(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """List all cars in the shop"""
    query = db.query(Car).filter(Car.shop_id == current_staff.shop_id)
    
    if search:
        query = query.filter(
            (Car.make.ilike(f"%{search}%")) |
            (Car.model.ilike(f"%{search}%")) |
            (Car.license_plate.ilike(f"%{search}%")) |
            (Car.vin.ilike(f"%{search}%"))
        )
    
    cars = query.offset(skip).limit(limit).all()
    return cars


@router.get("/my-cars", response_model=List[CarSchema])
def get_my_cars(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get current customer's cars"""
    cars = db.query(Car).filter(
        Car.owner_id == current_customer.id,
        Car.shop_id == current_customer.shop_id
    ).all()
    
    return cars


@router.get("/{car_id}", response_model=CarWithOwner)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get car by ID"""
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.shop_id == current_staff.shop_id
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return car


@router.put("/{car_id}", response_model=CarSchema)
def update_car(
    car_id: int,
    update_data: CarUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Update car (receptionist or higher)"""
    
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.shop_id == current_staff.shop_id
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(car, field, value)
    
    car.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(car)
    
    return car


@router.post("/{car_id}/transfer-ownership", response_model=CarSchema)
def transfer_car_ownership(
    car_id: int,
    transfer_data: CarOwnershipTransfer,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Transfer car ownership to another customer"""
    
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.shop_id == current_staff.shop_id
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Verify new owner exists and belongs to the same shop
    new_owner = db.query(Customer).filter(
        Customer.id == transfer_data.new_owner_id,
        Customer.shop_id == current_staff.shop_id
    ).first()
    
    if not new_owner:
        raise HTTPException(status_code=404, detail="New owner not found")
    
    # Log ownership transfer
    history = CarOwnershipHistory(
        car_id=car.id,
        previous_owner_id=car.owner_id,
        new_owner_id=transfer_data.new_owner_id,
        transferred_by_staff_id=current_staff.id,
        notes=transfer_data.notes
    )
    db.add(history)
    
    # Update car owner
    car.owner_id = transfer_data.new_owner_id
    car.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(car)
    
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Delete car (receptionist or higher)"""
    
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.shop_id == current_staff.shop_id
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Check if car has work orders
    from app.models import WorkOrder
    has_work_orders = db.query(WorkOrder).filter(WorkOrder.car_id == car.id).first()
    
    if has_work_orders:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete car with existing work orders. Consider marking it as inactive instead."
        )
    
    db.delete(car)
    db.commit()
    return None
