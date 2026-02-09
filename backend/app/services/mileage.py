from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Car, WorkOrder, ServiceReminder, Customer
from app.config import settings


class MileageService:
    """Service for mileage prediction and service reminders"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_average_km_per_day(self, car_id: int) -> Optional[float]:
        """
        Calculate average km/day for a car based on visit history
        Returns None if insufficient data (< 2 visits with mileage)
        """
        # Get all completed work orders with mileage for this car, ordered by date
        work_orders = (
            self.db.query(WorkOrder)
            .filter(
                WorkOrder.car_id == car_id,
                WorkOrder.status == "done",
                WorkOrder.mileage_at_intake.isnot(None)
            )
            .order_by(WorkOrder.created_at)
            .all()
        )
        
        if len(work_orders) < settings.MIN_VISITS_FOR_PREDICTION:
            return None
        
        # Calculate average km/day between first and last visit
        first_visit = work_orders[0]
        last_visit = work_orders[-1]
        
        mileage_diff = last_visit.mileage_at_intake - first_visit.mileage_at_intake
        days_diff = (last_visit.created_at - first_visit.created_at).days
        
        if days_diff == 0:
            return None
        
        avg_km_per_day = mileage_diff / days_diff
        return max(0, avg_km_per_day)  # Ensure non-negative
    
    def predict_mileage(self, car_id: int, days_ahead: int = 14) -> Optional[int]:
        """
        Predict car mileage after specified days
        Returns None if prediction not possible
        """
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return None
        
        avg_km_per_day = self.calculate_average_km_per_day(car_id)
        if avg_km_per_day is None:
            return None
        
        predicted_mileage = car.current_mileage + int(avg_km_per_day * days_ahead)
        return predicted_mileage
    
    def needs_service_reminder(self, car_id: int) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Check if car needs service reminder
        Returns (needs_reminder, predicted_mileage, service_due_mileage)
        """
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return False, None, None
        
        predicted_mileage = self.predict_mileage(car_id, settings.SERVICE_REMINDER_DAYS_AHEAD)
        if predicted_mileage is None:
            return False, None, None
        
        # Calculate next service due mileage
        last_service_mileage = car.current_mileage - (car.current_mileage % car.service_interval_km)
        service_due_mileage = last_service_mileage + car.service_interval_km
        
        # Check if predicted mileage will reach or exceed service interval
        needs_reminder = predicted_mileage >= service_due_mileage
        
        return needs_reminder, predicted_mileage, service_due_mileage
    
    def check_all_cars_for_reminders(self, shop_id: int) -> List[dict]:
        """
        Check all cars in a shop for service reminders
        Returns list of cars that need reminders
        """
        cars = self.db.query(Car).filter(
            Car.shop_id == shop_id,
            Car.service_interval_km > 0
        ).all()
        
        cars_needing_reminders = []
        
        for car in cars:
            # Check if already sent reminder recently (within last 30 days)
            recent_reminder = (
                self.db.query(ServiceReminder)
                .filter(
                    ServiceReminder.car_id == car.id,
                    ServiceReminder.reminder_sent == True,
                    ServiceReminder.reminder_sent_at >= datetime.utcnow() - timedelta(days=30)
                )
                .first()
            )
            
            if recent_reminder:
                continue  # Skip if reminder sent recently
            
            needs_reminder, predicted_km, service_due_km = self.needs_service_reminder(car.id)
            
            if needs_reminder:
                # Create or get reminder record
                reminder = (
                    self.db.query(ServiceReminder)
                    .filter(
                        ServiceReminder.car_id == car.id,
                        ServiceReminder.reminder_sent == False
                    )
                    .first()
                )
                
                if not reminder:
                    reminder = ServiceReminder(
                        car_id=car.id,
                        customer_id=car.owner_id,
                        predicted_mileage=predicted_km,
                        service_due_mileage=service_due_km,
                        reminder_sent=False
                    )
                    self.db.add(reminder)
                    self.db.commit()
                    self.db.refresh(reminder)
                
                cars_needing_reminders.append({
                    "car": car,
                    "customer": car.owner,
                    "predicted_mileage": predicted_km,
                    "service_due_mileage": service_due_km,
                    "reminder_id": reminder.id
                })
        
        return cars_needing_reminders
    
    def mark_reminder_sent(self, reminder_id: int):
        """Mark a service reminder as sent"""
        reminder = self.db.query(ServiceReminder).filter(ServiceReminder.id == reminder_id).first()
        if reminder:
            reminder.reminder_sent = True
            reminder.reminder_sent_at = datetime.utcnow()
            self.db.commit()
    
    def update_car_mileage(self, car_id: int, new_mileage: int):
        """Update car's current mileage"""
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if car and new_mileage > car.current_mileage:
            car.current_mileage = new_mileage
            car.updated_at = datetime.utcnow()
            self.db.commit()


def get_mileage_service(db: Session) -> MileageService:
    """Dependency to get mileage service instance"""
    return MileageService(db)
