"""
Tests for work order status transitions and car_id filtering
"""
import pytest
from fastapi import status
from app.models import WorkOrder, Car, WorkOrderStatus


class TestWorkOrderStatusTransitions:
    """Test work order status update functionality"""
    
    def test_update_status_to_in_progress_sets_started_at(self, client, db, test_staff, test_shop, test_customer):
        """Test that updating status to in_progress automatically sets started_at"""
        # Create a car
        car = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Toyota",
            model="Camry",
            license_plate="TEST123",
            current_mileage=50000
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        
        # Create a work order
        work_order = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car.id,
            reported_issues="Engine noise",
            status=WorkOrderStatus.CREATED
        )
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Update status to in_progress
        response = client.put(
            f"/api/work-orders/{work_order.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "in_progress"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["started_at"] is not None
    
    def test_update_status_to_done_sets_completed_at(self, client, db, test_staff, test_shop, test_customer):
        """Test that updating status to done automatically sets completed_at"""
        # Create a car
        car = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Honda",
            model="Civic",
            license_plate="TEST456",
            current_mileage=60000
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        
        # Create a work order
        work_order = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car.id,
            reported_issues="Oil change needed",
            status=WorkOrderStatus.IN_PROGRESS,
            mileage_at_intake=65000
        )
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Update status to done
        response = client.put(
            f"/api/work-orders/{work_order.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "done"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "done"
        assert data["completed_at"] is not None
        
        # Verify car mileage was updated
        db.refresh(car)
        assert car.current_mileage == 65000
    
    def test_update_work_order_notes(self, client, db, test_staff, test_shop, test_customer):
        """Test updating diagnostic_notes and mechanic_notes"""
        # Create a car
        car = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Ford",
            model="F-150",
            license_plate="TEST789",
            current_mileage=80000
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        
        # Create a work order
        work_order = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car.id,
            reported_issues="Brake squeaking",
            status=WorkOrderStatus.DIAGNOSING
        )
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Update notes
        response = client.put(
            f"/api/work-orders/{work_order.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "diagnostic_notes": "Brake pads worn out",
                "mechanic_notes": "Replaced front brake pads"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["diagnostic_notes"] == "Brake pads worn out"
        assert data["mechanic_notes"] == "Replaced front brake pads"


class TestWorkOrderCarIdFilter:
    """Test car_id filtering in work order list endpoint"""
    
    def test_filter_work_orders_by_car_id(self, client, db, test_staff, test_shop, test_customer):
        """Test filtering work orders by car_id"""
        # Create two cars
        car1 = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Toyota",
            model="Corolla",
            license_plate="CAR001",
            current_mileage=40000
        )
        car2 = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Honda",
            model="Accord",
            license_plate="CAR002",
            current_mileage=50000
        )
        db.add_all([car1, car2])
        db.commit()
        db.refresh(car1)
        db.refresh(car2)
        
        # Create work orders for both cars
        wo1 = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car1.id,
            reported_issues="Issue 1",
            status=WorkOrderStatus.CREATED
        )
        wo2 = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car1.id,
            reported_issues="Issue 2",
            status=WorkOrderStatus.DONE
        )
        wo3 = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car2.id,
            reported_issues="Issue 3",
            status=WorkOrderStatus.CREATED
        )
        db.add_all([wo1, wo2, wo3])
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Filter by car1
        response = client.get(
            "/api/work-orders",
            params={"car_id": car1.id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(wo["car_id"] == car1.id for wo in data)
        
        # Filter by car2
        response = client.get(
            "/api/work-orders",
            params={"car_id": car2.id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["car_id"] == car2.id
