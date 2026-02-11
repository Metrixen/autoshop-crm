from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import SMSLog as SMSLogModel, Staff
from app.schemas import SMSLog
from app.utils.auth import get_receptionist_or_higher

router = APIRouter(prefix="/api/sms-logs", tags=["SMS Logs"])


@router.get("", response_model=List[SMSLog])
def list_sms_logs(
    skip: int = 0,
    limit: int = 100,
    recipient_phone: Optional[str] = None,
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """
    List SMS logs for the current shop
    
    Requires receptionist or higher role
    
    Filters:
    - recipient_phone: Filter by recipient phone number
    - message_type: Filter by message type (welcome, appointment_confirmed, car_ready, service_reminder)
    - status: Filter by status (sent, delivered, failed)
    """
    
    query = db.query(SMSLogModel).filter(SMSLogModel.shop_id == current_staff.shop_id)
    
    if recipient_phone:
        query = query.filter(SMSLogModel.recipient_phone == recipient_phone)
    
    if message_type:
        query = query.filter(SMSLogModel.message_type == message_type)
    
    if status:
        query = query.filter(SMSLogModel.status == status)
    
    sms_logs = query.order_by(SMSLogModel.sent_at.desc()).offset(skip).limit(limit).all()
    
    return sms_logs
