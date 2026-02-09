"""
Seed database with realistic demo data
Run with: python -m app.seed
"""
from datetime import datetime, timedelta
import random
from faker import Faker
from app.database import SessionLocal, init_db
from app.models import (
    Shop, Staff, Customer, Car, WorkOrder, WorkOrderLineItem, 
    Invoice, Appointment, UserRole, WorkOrderStatus, InvoiceStatus, AppointmentStatus
)
from app.utils.auth import get_password_hash

# Initialize Faker with Bulgarian locale
faker = Faker(['bg_BG'])
Faker.seed(42)
random.seed(42)

def create_seed_data():
    """Create seed data for demo/testing"""
    
    db = SessionLocal()
    
    try:
        print("Initializing database...")
        init_db()
        
        # Create Demo Shop
        print("Creating demo shop...")
        shop = Shop(
            name="AutoShop Sofia",
            address="бул. България 123, София 1618",
            phone="+359 2 987 6543",
            email="info@autoshop-sofia.bg",
            website="https://autoshop-sofia.bg",
            working_hours='{"monday": "8:00-18:00", "tuesday": "8:00-18:00", "wednesday": "8:00-18:00", "thursday": "8:00-18:00", "friday": "8:00-18:00", "saturday": "9:00-14:00", "sunday": "closed"}',
            number_of_bays=4,
            labor_rate_per_hour=80.0,
            online_payments_enabled=True,
            sms_enabled=True,
            mechanics_see_pricing=True,
            subscription_plan="professional",
            is_active=True,
            is_trial=False
        )
        db.add(shop)
        db.commit()
        db.refresh(shop)
        print(f"✓ Shop created: {shop.name} (ID: {shop.id})")
        
        # Create Super Admin
        print("\nCreating staff...")
        super_admin = Staff(
            shop_id=shop.id,
            username="admin",
            email="admin@autoshop.com",
            phone="+359888000000",
            first_name="Иван",
            last_name="Петров",
            role=UserRole.SUPER_ADMIN,
            password_hash=get_password_hash("admin123")
        )
        db.add(super_admin)
        
        # Create Manager
        manager = Staff(
            shop_id=shop.id,
            username="manager",
            email="manager@autoshop-sofia.bg",
            phone="+359888000001",
            first_name="Георги",
            last_name="Димитров",
            role=UserRole.MANAGER,
            password_hash=get_password_hash("manager123")
        )
        db.add(manager)
        
        # Create Receptionist
        receptionist = Staff(
            shop_id=shop.id,
            username="reception",
            email="reception@autoshop-sofia.bg",
            phone="+359888000002",
            first_name="Мария",
            last_name="Иванова",
            role=UserRole.RECEPTIONIST,
            password_hash=get_password_hash("reception123")
        )
        db.add(receptionist)
        
        # Create Mechanics
        mechanics = []
        mechanic_names = [
            ("Петър", "Василев", "Двигатели"),
            ("Стоян", "Георгиев", "Ходова част"),
            ("Красимир", "Тодоров", "Електрика"),
            ("Николай", "Христов", "Климатици"),
        ]
        
        for first, last, specialty in mechanic_names:
            mechanic = Staff(
                shop_id=shop.id,
                username=first.lower() + last.lower(),
                email=f"{first.lower()}.{last.lower()}@autoshop-sofia.bg",
                phone=f"+35988800000{len(mechanics)+3}",
                first_name=first,
                last_name=last,
                role=UserRole.MECHANIC,
                specialty=specialty,
                password_hash=get_password_hash("mechanic123")
            )
            db.add(mechanic)
            mechanics.append(mechanic)
        
        db.commit()
        print(f"✓ Created 1 super admin, 1 manager, 1 receptionist, {len(mechanics)} mechanics")
        
        # Create Customers
        print("\nCreating customers...")
        customers = []
        bulgarian_first_names = [
            "Иван", "Георги", "Димитър", "Николай", "Петър", "Стоян", "Христо", "Васил",
            "Мария", "Елена", "Йорданка", "Ивелина", "Надежда", "Виктория", "Десислава", "Антония"
        ]
        bulgarian_last_names = [
            "Иванов", "Георгиев", "Димитров", "Петров", "Николов", "Христов", "Стоянов", "Василев",
            "Тодоров", "Илиев", "Атанасов", "Костов", "Ангелов", "Господинов", "Маринов", "Колев"
        ]
        
        for i in range(50):
            first_name = random.choice(bulgarian_first_names)
            last_name = random.choice(bulgarian_last_names)
            
            customer = Customer(
                shop_id=shop.id,
                phone=f"+359888{100000 + i:06d}",
                email=f"{first_name.lower()}.{last_name.lower()}{i}@email.bg" if i % 3 == 0 else None,
                first_name=first_name,
                last_name=last_name,
                password_hash=get_password_hash(f"customer{i}"),
                gdpr_consent=True,
                gdpr_consent_date=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.add(customer)
            customers.append(customer)
        
        db.commit()
        print(f"✓ Created {len(customers)} customers")
        
        # Create Cars
        print("\nCreating cars...")
        car_makes_models = [
            ("BMW", ["320d", "525d", "X5", "X3", "118i"]),
            ("Mercedes-Benz", ["C220", "E200", "GLK", "A180", "CLA"]),
            ("Volkswagen", ["Golf", "Passat", "Tiguan", "Polo", "Jetta"]),
            ("Audi", ["A4", "A6", "Q5", "A3", "Q3"]),
            ("Opel", ["Astra", "Insignia", "Corsa", "Mokka", "Vectra"]),
            ("Skoda", ["Octavia", "Superb", "Fabia", "Kodiaq", "Rapid"]),
            ("Toyota", ["Corolla", "Avensis", "Auris", "RAV4", "Yaris"]),
            ("Renault", ["Megane", "Clio", "Scenic", "Captur", "Kadjar"]),
        ]
        
        license_plate_letters = ["А", "В", "Е", "К", "М", "Н", "О", "Р", "С", "Т", "У", "Х"]
        license_plate_cities = ["СА", "СВ", "РВ", "РР", "ВТ", "ВН", "ПК", "ЕВ", "РА", "КН"]
        
        cars = []
        for i in range(70):
            make, models = random.choice(car_makes_models)
            model = random.choice(models)
            year = random.randint(2010, 2024)
            
            # Generate Bulgarian license plate (e.g., "СА 1234 ВК")
            city = random.choice(license_plate_cities)
            number = random.randint(1000, 9999)
            letters = ''.join(random.choices(license_plate_letters, k=2))
            license_plate = f"{city} {number} {letters}"
            
            owner = random.choice(customers)
            
            car = Car(
                shop_id=shop.id,
                owner_id=owner.id,
                make=make,
                model=model,
                year=year,
                license_plate=license_plate,
                color=random.choice(["Черен", "Бял", "Сив", "Син", "Червен", "Сребърен"]),
                current_mileage=random.randint(50000, 250000),
                service_interval_km=random.choice([10000, 15000, 20000])
            )
            db.add(car)
            cars.append(car)
        
        db.commit()
        print(f"✓ Created {len(cars)} cars")
        
        # Create Work Orders, Line Items, and Invoices
        print("\nCreating work orders and invoices...")
        services = [
            ("Смяна на масло и филтри", "labor", 1, 50),
            ("Смяна на спирачни накладки предни", "labor", 1, 80),
            ("Смяна на спирачни накладки задни", "labor", 1, 60),
            ("Диагностика", "labor", 1, 40),
            ("Смяна на антифриз", "labor", 1, 30),
            ("Смяна на ангренаж", "labor", 1, 200),
            ("Смяна на свещи", "labor", 1, 40),
            ("Зареждане на климатик", "labor", 1, 80),
            ("Геометрия", "labor", 1, 40),
            ("Баланс на гуми", "labor", 1, 20),
        ]
        
        parts = [
            ("Моторно масло 5W-30 (5л)", "part", 1, 45),
            ("Маслен филтър", "part", 1, 12),
            ("Въздушен филтър", "part", 1, 15),
            ("Спирачни накладки", "part", 1, 80),
            ("Спирачен диск", "part", 2, 120),
            ("Антифриз (5л)", "part", 1, 25),
            ("Комплект ангренаж", "part", 1, 350),
            ("Свещи (комплект)", "part", 1, 60),
            ("Хладилен агент R134", "part", 1, 40),
        ]
        
        work_orders_count = 0
        invoices_count = 0
        
        # Create completed work orders (past)
        for i in range(45):
            car = random.choice(cars)
            customer = db.query(Customer).filter(Customer.id == car.owner_id).first()
            mechanic = random.choice(mechanics)
            
            days_ago = random.randint(1, 180)
            created_date = datetime.utcnow() - timedelta(days=days_ago)
            started_date = created_date + timedelta(hours=random.randint(1, 4))
            completed_date = started_date + timedelta(hours=random.randint(2, 8))
            
            wo = WorkOrder(
                shop_id=shop.id,
                customer_id=customer.id,
                car_id=car.id,
                assigned_mechanic_id=mechanic.id,
                status=WorkOrderStatus.DONE,
                reported_issues=random.choice([
                    "Странен шум от двигателя",
                    "Изтриване на спирачките",
                    "Редовна поддръжка",
                    "Запушен филтър за твърди частици",
                    "Проблем с климатика",
                    "Вибрации при скорости над 100 км/ч"
                ]),
                mileage_at_intake=car.current_mileage - random.randint(1000, 10000),
                diagnostic_notes="Диагностиката показа " + random.choice([
                    "износени спирачни накладки",
                    "стари филтри, нуждаещи се от смяна",
                    "нисък антифриз",
                    "неоригинално масло"
                ]),
                mechanic_notes="Извършена " + random.choice(["пълна проверка", "смяна на части", "диагностика"]),
                created_at=created_date,
                started_at=started_date,
                completed_at=completed_date
            )
            db.add(wo)
            db.flush()
            
            # Add line items
            num_services = random.randint(1, 3)
            selected_services = random.sample(services, min(num_services, len(services)))
            selected_parts = random.sample(parts, min(num_services, len(parts)))
            
            subtotal = 0.0
            for service_name, item_type, qty, price in selected_services:
                line_item = WorkOrderLineItem(
                    work_order_id=wo.id,
                    item_type=item_type,
                    description=service_name,
                    quantity=qty,
                    unit_price=price,
                    total_price=qty * price,
                    added_by_staff_id=mechanic.id
                )
                db.add(line_item)
                subtotal += line_item.total_price
            
            for part_name, item_type, qty, price in selected_parts:
                line_item = WorkOrderLineItem(
                    work_order_id=wo.id,
                    item_type=item_type,
                    description=part_name,
                    quantity=qty,
                    unit_price=price,
                    total_price=qty * price,
                    added_by_staff_id=mechanic.id
                )
                db.add(line_item)
                subtotal += line_item.total_price
            
            # Create invoice
            tax_rate = 0.20
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            invoice = Invoice(
                shop_id=shop.id,
                work_order_id=wo.id,
                customer_id=customer.id,
                invoice_number=f"INV-2024-{invoices_count+1:05d}",
                subtotal=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total=total,
                status=InvoiceStatus.PAID,
                payment_method=random.choice(["cash", "card", "online"]),
                finalized_at=completed_date,
                finalized_by_staff_id=receptionist.id,
                paid_at=completed_date + timedelta(hours=random.randint(1, 24)),
                created_at=completed_date
            )
            db.add(invoice)
            
            work_orders_count += 1
            invoices_count += 1
        
        # Create active work orders
        statuses = [WorkOrderStatus.CREATED, WorkOrderStatus.DIAGNOSING, WorkOrderStatus.IN_PROGRESS]
        for status in statuses:
            for i in range(3):
                car = random.choice(cars)
                customer = db.query(Customer).filter(Customer.id == car.owner_id).first()
                mechanic = random.choice(mechanics)
                
                created_date = datetime.utcnow() - timedelta(days=random.randint(0, 5))
                
                wo = WorkOrder(
                    shop_id=shop.id,
                    customer_id=customer.id,
                    car_id=car.id,
                    assigned_mechanic_id=mechanic.id,
                    status=status,
                    reported_issues=random.choice([
                        "Червена лампичка на таблото",
                        "Странен звук при завой",
                        "Редовна поддръжка 15000 км",
                        "Проблем с електрониката"
                    ]),
                    mileage_at_intake=car.current_mileage,
                    created_at=created_date,
                    started_at=created_date + timedelta(hours=2) if status != WorkOrderStatus.CREATED else None
                )
                db.add(wo)
                work_orders_count += 1
        
        db.commit()
        print(f"✓ Created {work_orders_count} work orders and {invoices_count} invoices")
        
        # Create Appointments
        print("\nCreating appointments...")
        appointments_count = 0
        
        # Requested appointments
        for i in range(5):
            customer = random.choice(customers)
            customer_cars = [c for c in cars if c.owner_id == customer.id]
            car = random.choice(customer_cars) if customer_cars else None
            
            appointment = Appointment(
                shop_id=shop.id,
                customer_id=customer.id,
                car_id=car.id if car else None,
                unregistered_car_details="Ford Focus 2015" if not car else None,
                issue_description=random.choice([
                    "Нужда от редовна поддръжка",
                    "Странен шум от двигателя",
                    "Спирачките скърцат",
                    "Нужда от смяна на гуми"
                ]),
                preferred_date=datetime.utcnow() + timedelta(days=random.randint(1, 7)),
                preferred_time=random.choice(["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]),
                status=AppointmentStatus.REQUESTED
            )
            db.add(appointment)
            appointments_count += 1
        
        # Confirmed appointments
        for i in range(8):
            customer = random.choice(customers)
            customer_cars = [c for c in cars if c.owner_id == customer.id]
            car = random.choice(customer_cars) if customer_cars else None
            
            appointment = Appointment(
                shop_id=shop.id,
                customer_id=customer.id,
                car_id=car.id if car else None,
                issue_description=random.choice([
                    "Годишен преглед",
                    "Смяна на масло",
                    "Проблем с климатика",
                    "Смяна на ангренаж"
                ]),
                preferred_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                preferred_time=random.choice(["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]),
                status=AppointmentStatus.CONFIRMED,
                confirmed_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                confirmed_by_staff_id=receptionist.id,
                sms_sent=True,
                sms_sent_at=datetime.utcnow()
            )
            db.add(appointment)
            appointments_count += 1
        
        db.commit()
        print(f"✓ Created {appointments_count} appointments")
        
        print("\n" + "="*50)
        print("✓ Seed data created successfully!")
        print("="*50)
        print("\nDemo Credentials:")
        print("\nSuper Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nManager:")
        print("  Username: manager")
        print("  Password: manager123")
        print("\nReceptionist:")
        print("  Username: reception")
        print("  Password: reception123")
        print("\nMechanic:")
        print("  Username: петървасилев (or any mechanic username)")
        print("  Password: mechanic123")
        print("\nCustomer (example):")
        print("  Phone: +359888100000")
        print("  Password: customer0")
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\n✗ Error creating seed data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
