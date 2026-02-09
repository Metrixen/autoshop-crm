from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Shop, Staff, UserRole
from app.schemas import Shop as ShopSchema, ShopUpdate
from app.utils.auth import get_current_staff, get_manager

router = APIRouter(prefix="/api/shop", tags=["Shop"])


@router.get("/", response_model=ShopSchema)
def get_shop_settings(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get shop settings"""
    
    shop = db.query(Shop).filter(Shop.id == current_staff.shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return shop


@router.put("/", response_model=ShopSchema)
def update_shop_settings(
    update_data: ShopUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Update shop settings (manager or super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == current_staff.shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(shop, field, value)
    
    from datetime import datetime
    shop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(shop)
    
    return shop
