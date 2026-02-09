from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Staff, Customer, UserRole
from app.schemas import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    # Convert sub to string to comply with JWT spec
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    # Convert sub to string to comply with JWT spec
    if "sub" in to_encode and isinstance(to_encode["sub"], int):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        role: str = payload.get("role")
        shop_id: int = payload.get("shop_id")
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Convert string sub back to integer user_id
        user_id = int(user_id_str)
        return TokenData(user_id=user_id, role=UserRole(role), shop_id=shop_id)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from token"""
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Try to get staff user first
    user = db.query(Staff).filter(Staff.id == token_data.user_id).first()
    if user:
        return user
    
    # Try customer
    user = db.query(Customer).filter(Customer.id == token_data.user_id).first()
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")


def get_current_staff(current_user=Depends(get_current_user)) -> Staff:
    """Ensure current user is staff member"""
    if not isinstance(current_user, Staff):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required")
    return current_user


def get_current_customer(current_user=Depends(get_current_user)) -> Customer:
    """Ensure current user is customer"""
    if not isinstance(current_user, Customer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")
    return current_user


def require_role(*allowed_roles: UserRole):
    """Decorator to require specific user roles"""
    def role_checker(current_user=Depends(get_current_staff)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def get_super_admin(current_user: Staff = Depends(get_current_staff)) -> Staff:
    """Ensure current user is super admin"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return current_user


def get_manager(current_user: Staff = Depends(get_current_staff)) -> Staff:
    """Ensure current user is manager or super admin"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")
    return current_user


def get_receptionist_or_higher(current_user: Staff = Depends(get_current_staff)) -> Staff:
    """Ensure current user is receptionist, manager, or super admin"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER, UserRole.RECEPTIONIST]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Receptionist access required")
    return current_user
