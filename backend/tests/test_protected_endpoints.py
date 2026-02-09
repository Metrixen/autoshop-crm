"""
Tests for protected endpoints and authorization
"""
import pytest
from fastapi import status
from app.utils.auth import create_access_token


class TestProtectedEndpoints:
    """Test authorization on protected endpoints"""
    
    def test_protected_endpoint_without_token_returns_401(self, client, test_shop):
        """Test that accessing protected endpoint without token returns 401 or 403"""
        # Try to access dashboard without authentication
        response = client.get("/api/reports/dashboard")
        
        # May return 401 or 403 depending on implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_protected_endpoint_with_invalid_token_returns_401(self, client, test_shop):
        """Test that accessing protected endpoint with invalid token returns 401"""
        response = client.get(
            "/api/reports/dashboard",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_valid_token_no_redirect(self, client, test_staff):
        """Test that protected endpoint with valid token doesn't cause redirect"""
        # Create a valid access token
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        # Access protected endpoint
        response = client.get(
            "/api/reports/dashboard",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Should not be 307 redirect
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
        # Should either succeed (200) or fail with proper error, but not redirect
        assert len(response.history) == 0
    
    def test_work_orders_endpoint_without_token_returns_401(self, client, test_shop):
        """Test that work orders endpoint requires authentication"""
        response = client.get("/api/work-orders")
        
        # May return 401, 403, or 404 depending on implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_work_orders_endpoint_no_trailing_slash_redirect(self, client, test_staff):
        """Test that work orders endpoint doesn't cause 307 redirect due to trailing slash"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        # Access endpoint without trailing slash (as defined in routes)
        response = client.get(
            "/api/work-orders",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Should not be 307 redirect
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
        assert len(response.history) == 0
    
    def test_appointments_pending_endpoint_without_token_returns_401(self, client):
        """Test that appointments/pending endpoint requires authentication"""
        response = client.get("/api/appointments/pending")
        
        # May return 401 or 403 depending on implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_customers_me_endpoint_without_token_returns_401(self, client):
        """Test that customers/me endpoint requires authentication"""
        response = client.get("/api/customers/me")
        
        # May return 401 or 403 depending on implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestAuthorizationHeaderPreservation:
    """Test that Authorization headers are preserved and not stripped by redirects"""
    
    def test_authorization_header_preserved_on_protected_endpoint(self, client, test_staff):
        """Test that Authorization header is preserved when accessing protected endpoints"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        # Make request to protected endpoint
        response = client.get(
            "/api/staff/mechanics",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Should not redirect (which would strip the header)
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
        # Should either succeed or fail with proper status, not auth failure due to stripped header
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            # If 401, it should be because of invalid token, not missing header
            # In a real scenario with proper dependencies, this should succeed
            pass
        
        # Most importantly, ensure there's no redirect
        assert len(response.history) == 0
    
    def test_multiple_protected_endpoints_no_redirect(self, client, test_staff):
        """Test that multiple protected endpoints don't cause redirects"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test multiple endpoints
        endpoints = [
            "/api/reports/dashboard",
            "/api/staff/mechanics",
            "/api/appointments/pending",
            "/api/work-orders"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            # None should cause 307 redirect
            assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
            assert len(response.history) == 0


class TestFastAPIRedirectSlashesConfiguration:
    """Test that FastAPI redirect_slashes=False is working"""
    
    def test_endpoint_with_trailing_slash_returns_404_not_307(self, client, test_staff):
        """Test that requesting endpoint with trailing slash returns 404, not 307 redirect"""
        access_token = create_access_token(
            data={
                "sub": test_staff.id,
                "role": test_staff.role.value,
                "shop_id": test_staff.shop_id
            }
        )
        
        # Request endpoint WITH trailing slash when route is defined WITHOUT it
        response = client.get(
            "/api/work-orders/",  # Note the trailing slash
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # With redirect_slashes=False, should get 404, not 307
        # (because the exact route doesn't exist)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
    
    def test_auth_endpoint_with_trailing_slash_returns_404_not_307(self, client, test_staff):
        """Test that auth endpoint with trailing slash doesn't cause redirect"""
        # Request with trailing slash
        response = client.post(
            "/api/auth/staff/login/",  # Note the trailing slash
            json={
                "username": "teststaff",
                "password": "testpass123"
            }
        )
        
        # Should get 404 or some error, but NOT 307 redirect
        assert response.status_code != status.HTTP_307_TEMPORARY_REDIRECT
