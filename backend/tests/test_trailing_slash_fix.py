"""
Tests for trailing slash fix and API endpoint integration
"""
import pytest
from fastapi import status
from app.utils.auth import create_access_token, verify_password, get_password_hash
from app.models import UserRole, Car


class TestTrailingSlashFix:
    """Test that all list and create endpoints work without trailing slashes"""
    
    def test_work_orders_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/work-orders?limit=5 does not redirect"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/work-orders?limit=5",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Should NOT be a redirect
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
        assert len(response.history) == 0  # No redirects
        # Should get 200 OK for successful request
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_appointments_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/appointments?limit=5 returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/appointments?limit=5",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_cars_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/cars returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/cars",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_customers_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/customers returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/customers",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_invoices_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/invoices returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/invoices",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_staff_list_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/staff returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/staff",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_shop_get_endpoint_without_trailing_slash(self, client, test_staff):
        """Test GET /api/shop returns 200"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        response = client.get(
            "/api/shop",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert "name" in response.json()


class TestBcryptPasslibCompatibility:
    """Test that bcrypt and passlib work correctly for password hashing"""
    
    def test_password_hashing_works(self):
        """Test that password hashing works with bcrypt 4.0.1"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Hash should be a string
        assert isinstance(hashed, str)
        # Hash should start with bcrypt prefix
        assert hashed.startswith("$2b$")
        # Hash should be reasonably long
        assert len(hashed) > 50
    
    def test_password_verification_works(self):
        """Test that password verification works"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("WrongPassword", hashed) is False
    
    def test_multiple_hashes_are_different(self):
        """Test that hashing the same password twice produces different hashes"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestCustomerLoginAndAPIAccess:
    """Test customer login and subsequent API calls"""
    
    def test_customer_login_and_access_my_cars(self, client, test_customer, db, test_shop):
        """Test customer can login and access /api/cars/my-cars"""
        # Step 1: Login
        login_response = client.post(
            "/api/auth/customer/login",
            json={
                "username": test_customer.phone,
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        access_token = data["access_token"]
        
        # Step 2: Access /api/cars/my-cars
        response = client.get(
            "/api/cars/my-cars",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)
    
    def test_customer_login_and_access_work_orders(self, client, test_customer):
        """Test customer can login and access /api/work-orders"""
        # Login
        login_response = client.post(
            "/api/auth/customer/login",
            json={
                "username": test_customer.phone,
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Access work orders
        response = client.get(
            "/api/work-orders",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
    
    def test_customer_login_and_access_appointments(self, client, test_customer):
        """Test customer can login and access /api/appointments"""
        # Login
        login_response = client.post(
            "/api/auth/customer/login",
            json={
                "username": test_customer.phone,
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Access appointments
        response = client.get(
            "/api/appointments",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0


class TestStaffLoginAndAPIAccess:
    """Test staff login and subsequent API calls"""
    
    def test_staff_login_and_access_dashboard(self, client, test_staff):
        """Test staff can login and access /api/reports/dashboard"""
        # Login
        login_response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff",
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Access dashboard
        response = client.get(
            "/api/reports/dashboard",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        data = response.json()
        assert "total_customers" in data
        assert "active_work_orders" in data
    
    def test_staff_login_and_access_work_orders(self, client, test_staff):
        """Test staff can login and access /api/work-orders"""
        # Login
        login_response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff",
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Access work orders
        response = client.get(
            "/api/work-orders",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
    
    def test_staff_login_and_access_appointments_pending(self, client, db, test_shop):
        """Test staff can login and access /api/appointments/pending"""
        # Create staff with receptionist role to access pending appointments
        from app.models import Staff
        from app.utils.auth import get_password_hash
        
        receptionist = Staff(
            shop_id=test_shop.id,
            username="receptionist",
            email="receptionist@test.com",
            phone="+1234567894",
            password_hash=get_password_hash("testpass123"),
            first_name="Test",
            last_name="Receptionist",
            role=UserRole.RECEPTIONIST,
            is_active=True
        )
        db.add(receptionist)
        db.commit()
        db.refresh(receptionist)
        
        # Login
        login_response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "receptionist",
                "password": "testpass123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Access pending appointments
        response = client.get(
            "/api/appointments/pending",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.history) == 0
        assert isinstance(response.json(), list)


class TestEndpointStatusCodes:
    """Test that endpoints return correct status codes, not 404"""
    
    def test_all_list_endpoints_return_200_not_404(self, client, test_staff):
        """Test that all list endpoints return 200, not 404"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        endpoints = [
            "/api/work-orders",
            "/api/appointments",
            "/api/cars",
            "/api/customers",
            "/api/invoices",
            "/api/staff",
            "/api/shop"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            # Should NOT be 404
            assert response.status_code != status.HTTP_404_NOT_FOUND, f"{endpoint} returned 404"
            # Should be 200 for all these endpoints
            assert response.status_code == status.HTTP_200_OK, f"{endpoint} did not return 200"
