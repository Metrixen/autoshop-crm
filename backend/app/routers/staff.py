from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Staff, UserRole
from app.schemas import Staff as StaffSchema, StaffCreate, StaffUpdate
from app.utils.auth import get_current_staff, get_manager, get_password_hash

router = APIRouter(prefix="/api/staff", tags=["Staff"])


@router.post("/", response_model=StaffSchema, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Create new staff member (manager or super admin only)"""
    
    # Check if username/email/phone already exists
    existing = db.query(Staff).filter(
        (Staff.username == staff_data.username) |
        (Staff.email == staff_data.email) |
        (Staff.phone == staff_data.phone)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username, email, or phone already exists")
    
    # Only super admin can create other super admins
    if staff_data.role == UserRole.SUPER_ADMIN and current_staff.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create other super admins")
    
    staff = Staff(
        shop_id=staff_data.shop_id,
        username=staff_data.username,
        email=staff_data.email,
        phone=staff_data.phone,
        first_name=staff_data.first_name,
        last_name=staff_data.last_name,
        role=staff_data.role,
        specialty=staff_data.specialty,
        password_hash=get_password_hash(staff_data.password)
    )
    
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    return staff


@router.get("/", response_model=List[StaffSchema])
def list_staff(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """List all staff in the shop"""
    
    staff_list = db.query(Staff).filter(
        Staff.shop_id == current_staff.shop_id,
        Staff.is_active == True
    ).offset(skip).limit(limit).all()
    
    return staff_list


@router.get("/mechanics", response_model=List[StaffSchema])
def list_mechanics(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """List all mechanics in the shop"""
    
    mechanics = db.query(Staff).filter(
        Staff.shop_id == current_staff.shop_id,
        Staff.role == UserRole.MECHANIC,
        Staff.is_active == True
    ).all()
    
    return mechanics


@router.get("/{staff_id}", response_model=StaffSchema)
def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get staff by ID"""
    
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.shop_id == current_staff.shop_id
    ).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    return staff


@router.put("/{staff_id}", response_model=StaffSchema)
def update_staff(
    staff_id: int,
    update_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Update staff member (manager or super admin only)"""
    
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.shop_id == current_staff.shop_id
    ).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(staff, field, value)
    
    from datetime import datetime
    staff.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(staff)
    
    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Deactivate staff member (soft delete)"""
    
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.shop_id == current_staff.shop_id
    ).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Don't allow deactivating self
    if staff.id == current_staff.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    staff.is_active = False
    db.commit()
    return None
