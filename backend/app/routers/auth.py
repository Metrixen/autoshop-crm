from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Staff, Customer, UserRole
from app.schemas import Token, LoginRequest
from app.utils.auth import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/staff/login", response_model=Token)
def staff_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Staff login endpoint (username/email + password)"""
    
    # Try to find staff by username, email, or phone
    staff = db.query(Staff).filter(
        (Staff.username == login_data.username) |
        (Staff.email == login_data.username) |
        (Staff.phone == login_data.username)
    ).first()
    
    if not staff or not verify_password(login_data.password, staff.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": staff.id, "role": staff.role.value, "shop_id": staff.shop_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": staff.id, "role": staff.role.value, "shop_id": staff.shop_id}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/customer/login", response_model=Token)
def customer_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Customer login endpoint (phone + password)"""
    
    # Find customer by phone
    customer = db.query(Customer).filter(Customer.phone == login_data.username).first()
    
    if not customer or not verify_password(login_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password"
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": customer.id, "role": UserRole.CUSTOMER.value, "shop_id": customer.shop_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": customer.id, "role": UserRole.CUSTOMER.value, "shop_id": customer.shop_id}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)
