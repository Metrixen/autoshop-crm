from typing import Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.orm import Session
from app.config import settings
from app.models import SMSLog, Shop


class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        if settings.SMS_ENABLED and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def _log_sms(self, shop_id: int, recipient_phone: str, message_type: str, 
                 message_body: str, twilio_sid: Optional[str] = None, 
                 status: str = "sent", error_message: Optional[str] = None):
        """Log SMS message to database"""
        sms_log = SMSLog(
            shop_id=shop_id,
            recipient_phone=recipient_phone,
            message_type=message_type,
            message_body=message_body,
            twilio_sid=twilio_sid,
            status=status,
            error_message=error_message
        )
        self.db.add(sms_log)
        
        # Increment shop SMS usage count
        shop = self.db.query(Shop).filter(Shop.id == shop_id).first()
        if shop:
            shop.sms_usage_count += 1
        
        self.db.commit()
    
    def send_sms(self, shop_id: int, recipient_phone: str, message_body: str, 
                 message_type: str = "generic") -> bool:
        """
        Send SMS message
        Returns True if successful, False otherwise
        """
        if not self.client:
            # Log as failed if SMS not configured
            self._log_sms(shop_id, recipient_phone, message_type, message_body, 
                         status="failed", error_message="SMS service not configured")
            return False
        
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=recipient_phone
            )
            
            self._log_sms(shop_id, recipient_phone, message_type, message_body, 
                         twilio_sid=message.sid, status="sent")
            return True
            
        except TwilioRestException as e:
            self._log_sms(shop_id, recipient_phone, message_type, message_body, 
                         status="failed", error_message=str(e))
            return False
    
    def send_welcome_sms(self, shop_id: int, customer_phone: str, 
                        customer_name: str, password: str, shop_website: str) -> bool:
        """Send welcome SMS with auto-generated password"""
        message = (
            f"Добре дошли в {settings.SHOP_NAME}! "
            f"Вашият профил е създаден.\n"
            f"Телефон: {customer_phone}\n"
            f"Парола: {password}\n"
            f"Влезте на: {shop_website}"
        )
        return self.send_sms(shop_id, customer_phone, message, "welcome")
    
    def send_appointment_confirmed_sms(self, shop_id: int, customer_phone: str, 
                                      customer_name: str, date: datetime, 
                                      shop_website: str) -> bool:
        """Send appointment confirmation SMS"""
        date_str = date.strftime("%d.%m.%Y в %H:%M")
        message = (
            f"Здравейте {customer_name},\n"
            f"Вашата среща е потвърдена за {date_str}.\n"
            f"{settings.SHOP_NAME}\n"
            f"Тел: {settings.SHOP_PHONE}\n"
            f"{shop_website}"
        )
        return self.send_sms(shop_id, customer_phone, message, "appointment_confirmed")
    
    def send_car_ready_sms(self, shop_id: int, customer_phone: str, 
                          customer_name: str, car_info: str, total: float, 
                          shop_website: str) -> bool:
        """Send car ready notification SMS"""
        message = (
            f"Здравейте {customer_name},\n"
            f"Вашият {car_info} е готов!\n"
            f"Сума: {total:.2f} лв.\n"
            f"{settings.SHOP_NAME}\n"
            f"{shop_website}"
        )
        return self.send_sms(shop_id, customer_phone, message, "car_ready")
    
    def send_service_reminder_sms(self, shop_id: int, customer_phone: str, 
                                 customer_name: str, car_info: str, 
                                 predicted_km: int, shop_website: str) -> bool:
        """Send proactive service reminder SMS"""
        message = (
            f"Здравейте {customer_name},\n"
            f"Вашият {car_info} скоро ще достигне {predicted_km} km и "
            f"е време за сервизно обслужване.\n"
            f"Запазете час на: {shop_website}\n"
            f"{settings.SHOP_NAME} | {settings.SHOP_PHONE}"
        )
        return self.send_sms(shop_id, customer_phone, message, "service_reminder")
    
    def send_password_reset_sms(self, shop_id: int, customer_phone: str, 
                               reset_code: str, shop_website: str) -> bool:
        """Send password reset code SMS"""
        message = (
            f"Вашият код за възстановяване на парола: {reset_code}\n"
            f"Или използвайте: {shop_website}/reset-password?code={reset_code}\n"
            f"{settings.SHOP_NAME}"
        )
        return self.send_sms(shop_id, customer_phone, message, "password_reset")


def get_sms_service(db: Session) -> SMSService:
    """Dependency to get SMS service instance"""
    return SMSService(db)
