"""
Tests for car service history endpoint
"""
import pytest
from fastapi import status
from app.models import Car, WorkOrder, CarOwnershipHistory, WorkOrderStatus, Customer


class TestCarServiceHistory:
    """Test GET /api/cars/{car_id}/service-history endpoint"""
    
    def test_get_service_history_returns_work_orders_and_ownership(self, client, db, test_staff, test_shop, test_customer):
        """Test that service history includes work orders and ownership history"""
        # Create a car
        car = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="BMW",
            model="X5",
            license_plate="BMW123",
            current_mileage=75000
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        
        # Create work orders
        wo1 = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car.id,
            reported_issues="Regular service",
            status=WorkOrderStatus.DONE,
            mileage_at_intake=70000
        )
        wo2 = WorkOrder(
            shop_id=test_shop.id,
            customer_id=test_customer.id,
            car_id=car.id,
            reported_issues="Tire replacement",
            status=WorkOrderStatus.DONE,
            mileage_at_intake=73000
        )
        db.add_all([wo1, wo2])
        db.commit()
        
        # Create another customer for ownership transfer
        customer2 = Customer(
            shop_id=test_shop.id,
            phone="+9876543210",
            email="customer2@test.com",
            password_hash="hash",
            first_name="Another",
            last_name="Customer",
            is_active=True
        )
        db.add(customer2)
        db.commit()
        db.refresh(customer2)
        
        # Create ownership history
        ownership = CarOwnershipHistory(
            car_id=car.id,
            previous_owner_id=None,
            new_owner_id=test_customer.id,
            transferred_by_staff_id=test_staff.id,
            notes="Initial registration"
        )
        db.add(ownership)
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Get service history
        response = client.get(
            f"/api/cars/{car.id}/service-history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify structure
        assert "car" in data
        assert "work_orders" in data
        assert "ownership_history" in data
        
        # Verify car details
        assert data["car"]["id"] == car.id
        assert data["car"]["make"] == "BMW"
        assert data["car"]["model"] == "X5"
        
        # Verify work orders
        assert len(data["work_orders"]) == 2
        assert any(wo["reported_issues"] == "Regular service" for wo in data["work_orders"])
        assert any(wo["reported_issues"] == "Tire replacement" for wo in data["work_orders"])
        
        # Verify ownership history
        assert len(data["ownership_history"]) == 1
        assert data["ownership_history"][0]["notes"] == "Initial registration"
    
    def test_get_service_history_for_nonexistent_car_returns_404(self, client, test_staff):
        """Test that requesting service history for non-existent car returns 404"""
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to get service history for non-existent car
        response = client.get(
            "/api/cars/99999/service-history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_service_history_empty_for_new_car(self, client, db, test_staff, test_shop, test_customer):
        """Test that service history is empty for a car with no work orders"""
        # Create a new car with no work orders
        car = Car(
            shop_id=test_shop.id,
            owner_id=test_customer.id,
            make="Tesla",
            model="Model 3",
            license_plate="TESLA1",
            current_mileage=0
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Get service history
        response = client.get(
            f"/api/cars/{car.id}/service-history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify empty work orders and ownership history
        assert data["car"]["id"] == car.id
        assert len(data["work_orders"]) == 0
        assert len(data["ownership_history"]) == 0
