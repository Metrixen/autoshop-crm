"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


class TestStaffLogin:
    """Test staff login endpoint"""
    
    def test_staff_login_with_valid_credentials_returns_tokens(self, client, test_staff):
        """Test staff login with valid username and password returns access and refresh tokens"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_staff_login_with_email_returns_tokens(self, client, test_staff):
        """Test staff login with email instead of username"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "staff@test.com",  # Using email as username
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_staff_login_with_phone_returns_tokens(self, client, test_staff):
        """Test staff login with phone number instead of username"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "+1234567891",  # Using phone as username
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_staff_login_with_invalid_username_returns_401(self, client, test_staff):
        """Test staff login with non-existent username returns 401"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "nonexistent",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]
    
    def test_staff_login_with_invalid_password_returns_401(self, client, test_staff):
        """Test staff login with wrong password returns 401"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]
    
    def test_staff_login_with_inactive_account_returns_403(self, client, inactive_staff):
        """Test staff login with inactive account returns 403"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "inactivestaff",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "Account is inactive" in data["detail"]
    
    def test_staff_login_with_missing_password_returns_422(self, client, test_staff):
        """Test staff login without password returns validation error"""
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCustomerLogin:
    """Test customer login endpoint"""
    
    def test_customer_login_with_valid_credentials_returns_tokens(self, client, test_customer):
        """Test customer login with valid phone and password returns tokens"""
        response = client.post(
            "/api/auth/customer/login",
            json={
                "username": "+1234567892",  # Phone number
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
    
    def test_customer_login_with_invalid_phone_returns_401(self, client, test_customer):
        """Test customer login with non-existent phone returns 401"""
        response = client.post(
            "/api/auth/customer/login",
            json={
                "username": "+9999999999",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Incorrect phone number or password" in data["detail"]
    
    def test_customer_login_with_invalid_password_returns_401(self, client, test_customer):
        """Test customer login with wrong password returns 401"""
        response = client.post(
            "/api/auth/customer/login",
            json={
                "username": "+1234567892",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Incorrect phone number or password" in data["detail"]


class TestAuthEndpointsNoRedirect:
    """Test that auth endpoints don't cause 307 redirects"""
    
    def test_staff_login_endpoint_no_trailing_slash_redirect(self, client, test_staff):
        """Test that staff login endpoint doesn't cause 307 redirect"""
        # The endpoint is defined without trailing slash, so this should work directly
        response = client.post(
            "/api/auth/staff/login",
            json={
                "username": "teststaff",
                "password": "testpass123"
            }
        )
        
        # Should get 200, not 307 redirect
        assert response.status_code == status.HTTP_200_OK
        # Ensure no redirect history
        assert len(response.history) == 0
    
    def test_customer_login_endpoint_no_trailing_slash_redirect(self, client, test_customer):
        """Test that customer login endpoint doesn't cause 307 redirect"""
        response = client.post(
            "/api/auth/customer/login",
            json={
                "username": "+1234567892",
                "password": "testpass123"
            }
        )
        
        # Should get 200, not 307 redirect
        assert response.status_code == status.HTTP_200_OK
        # Ensure no redirect history
        assert len(response.history) == 0
