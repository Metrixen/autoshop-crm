from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Shop, Staff, Customer, SMSLog, UserRole
from app.schemas import Shop as ShopSchema, ShopCreate
from app.utils.auth import get_super_admin, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


@router.post("/shops", response_model=ShopSchema, status_code=status.HTTP_201_CREATED)
def create_shop(
    shop_data: ShopCreate,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Create a new shop (super admin only)"""
    
    shop = Shop(**shop_data.dict())
    db.add(shop)
    db.commit()
    db.refresh(shop)
    
    return shop


@router.get("/shops", response_model=List[ShopSchema])
def list_all_shops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """List all shops (super admin only)"""
    
    shops = db.query(Shop).offset(skip).limit(limit).all()
    return shops


@router.get("/shops/{shop_id}", response_model=ShopSchema)
def get_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Get shop by ID (super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return shop


@router.put("/shops/{shop_id}/toggle-feature", response_model=ShopSchema)
def toggle_shop_feature(
    shop_id: int,
    feature: str,
    enabled: bool,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Toggle feature flag for a shop (super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Update feature flag
    if feature == "online_payments":
        shop.online_payments_enabled = enabled
    elif feature == "sms":
        shop.sms_enabled = enabled
    elif feature == "mechanics_pricing":
        shop.mechanics_see_pricing = enabled
    else:
        raise HTTPException(status_code=400, detail=f"Unknown feature: {feature}")
    
    shop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(shop)
    
    return shop


@router.put("/shops/{shop_id}/subscription", response_model=ShopSchema)
def update_shop_subscription(
    shop_id: int,
    plan: str,
    is_trial: bool = False,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Update shop subscription plan (super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop.subscription_plan = plan
    shop.is_trial = is_trial
    
    if is_trial and not shop.trial_ends_at:
        from datetime import timedelta
        shop.trial_ends_at = datetime.utcnow() + timedelta(days=30)
    elif not is_trial:
        shop.trial_ends_at = None
    
    shop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(shop)
    
    return shop


@router.put("/shops/{shop_id}/activate", response_model=ShopSchema)
def activate_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Activate shop (super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop.is_active = True
    shop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(shop)
    
    return shop


@router.put("/shops/{shop_id}/deactivate", response_model=ShopSchema)
def deactivate_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Deactivate shop (super admin only)"""
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop.is_active = False
    shop.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(shop)
    
    return shop


@router.get("/shops/{shop_id}/sms-usage")
def get_shop_sms_usage(
    shop_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Get SMS usage for a shop (super admin only)"""
    
    query = db.query(SMSLog).filter(SMSLog.shop_id == shop_id)
    
    if start_date:
        query = query.filter(SMSLog.sent_at >= start_date)
    if end_date:
        query = query.filter(SMSLog.sent_at <= end_date)
    
    logs = query.all()
    
    total_sent = len([log for log in logs if log.status in ["sent", "delivered"]])
    total_failed = len([log for log in logs if log.status == "failed"])
    
    return {
        "shop_id": shop_id,
        "total_sms": len(logs),
        "sent": total_sent,
        "failed": total_failed,
        "by_type": {}
    }


@router.post("/impersonate/{shop_id}")
def impersonate_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_admin: Staff = Depends(get_super_admin)
):
    """Impersonate shop admin (super admin only)"""
    
    # Find a manager or owner in the shop
    shop_manager = db.query(Staff).filter(
        Staff.shop_id == shop_id,
        Staff.role == UserRole.MANAGER,
        Staff.is_active == True
    ).first()
    
    if not shop_manager:
        raise HTTPException(status_code=404, detail="No active manager found in this shop")
    
    # Generate token for the shop manager
    from app.utils.auth import create_access_token, create_refresh_token
    
    access_token = create_access_token(
        data={"sub": shop_manager.id, "role": shop_manager.role.value, "shop_id": shop_manager.shop_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": shop_manager.id, "role": shop_manager.role.value, "shop_id": shop_manager.shop_id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "impersonated_user": {
            "id": shop_manager.id,
            "name": f"{shop_manager.first_name} {shop_manager.last_name}",
            "role": shop_manager.role.value,
            "shop_id": shop_manager.shop_id
        }
    }
