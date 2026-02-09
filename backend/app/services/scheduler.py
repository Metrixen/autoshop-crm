from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Shop
from app.services.mileage import MileageService
from app.services.sms import SMSService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def check_service_reminders():
    """
    Background job to check for service reminders
    Runs daily at configured time
    """
    logger.info(f"Running service reminder check at {datetime.now()}")
    
    db = SessionLocal()
    try:
        # Get all active shops
        shops = db.query(Shop).filter(Shop.is_active == True, Shop.sms_enabled == True).all()
        
        for shop in shops:
            logger.info(f"Checking service reminders for shop: {shop.name} (ID: {shop.id})")
            
            mileage_service = MileageService(db)
            sms_service = SMSService(db)
            
            # Get cars needing reminders
            cars_needing_reminders = mileage_service.check_all_cars_for_reminders(shop.id)
            
            logger.info(f"Found {len(cars_needing_reminders)} cars needing reminders")
            
            # Send reminders
            for item in cars_needing_reminders:
                car = item["car"]
                customer = item["customer"]
                predicted_km = item["predicted_mileage"]
                reminder_id = item["reminder_id"]
                
                car_info = f"{car.make} {car.model} ({car.license_plate})"
                customer_name = f"{customer.first_name} {customer.last_name}"
                
                # Send SMS
                success = sms_service.send_service_reminder_sms(
                    shop_id=shop.id,
                    customer_phone=customer.phone,
                    customer_name=customer_name,
                    car_info=car_info,
                    predicted_km=predicted_km,
                    shop_website=shop.website or settings.SHOP_WEBSITE
                )
                
                if success:
                    mileage_service.mark_reminder_sent(reminder_id)
                    logger.info(f"Sent reminder for car {car.id} to {customer.phone}")
                else:
                    logger.error(f"Failed to send reminder for car {car.id} to {customer.phone}")
        
    except Exception as e:
        logger.error(f"Error in service reminder check: {str(e)}")
    finally:
        db.close()


class SchedulerService:
    """Background job scheduler service"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        if not settings.ENABLE_SCHEDULER:
            logger.info("Scheduler is disabled")
            return
        
        # Daily service reminder check at configured hour
        self.scheduler.add_job(
            check_service_reminders,
            trigger=CronTrigger(hour=settings.MILEAGE_CHECK_HOUR, minute=0),
            id="service_reminders",
            name="Check service reminders",
            replace_existing=True
        )
        
        logger.info(f"Scheduled service reminder check at {settings.MILEAGE_CHECK_HOUR}:00 daily")
    
    def start(self):
        """Start the scheduler"""
        if not settings.ENABLE_SCHEDULER:
            return
        
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")


# Global scheduler instance
scheduler_service = SchedulerService()
