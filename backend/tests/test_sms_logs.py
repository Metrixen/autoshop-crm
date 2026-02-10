"""
Tests for SMS logs endpoint
"""
import pytest
from fastapi import status
from datetime import datetime
from app.models import SMSLog as SMSLogModel


class TestSMSLogsEndpoint:
    """Test GET /api/sms-logs endpoint"""
    
    def test_list_sms_logs_requires_auth(self, client):
        """Test that SMS logs endpoint requires authentication"""
        response = client.get("/api/sms-logs")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_sms_logs_returns_logs_for_shop(self, client, db, test_staff, test_shop):
        """Test listing SMS logs for the current shop"""
        # Create SMS logs
        sms1 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+1234567890",
            message_type="welcome",
            message_body="Welcome to our shop!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        sms2 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+1234567891",
            message_type="appointment_confirmed",
            message_body="Your appointment is confirmed.",
            status="delivered",
            sent_at=datetime.utcnow()
        )
        db.add_all([sms1, sms2])
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Get SMS logs
        response = client.get(
            "/api/sms-logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert any(log["message_type"] == "welcome" for log in data)
        assert any(log["message_type"] == "appointment_confirmed" for log in data)
    
    def test_filter_sms_logs_by_recipient_phone(self, client, db, test_staff, test_shop):
        """Test filtering SMS logs by recipient phone number"""
        # Create SMS logs
        sms1 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+1111111111",
            message_type="welcome",
            message_body="Welcome!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        sms2 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+2222222222",
            message_type="car_ready",
            message_body="Your car is ready!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        db.add_all([sms1, sms2])
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Filter by recipient_phone
        response = client.get(
            "/api/sms-logs",
            params={"recipient_phone": "+1111111111"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["recipient_phone"] == "+1111111111"
        assert data[0]["message_type"] == "welcome"
    
    def test_filter_sms_logs_by_message_type(self, client, db, test_staff, test_shop):
        """Test filtering SMS logs by message type"""
        # Create SMS logs
        sms1 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+1111111111",
            message_type="welcome",
            message_body="Welcome!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        sms2 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+2222222222",
            message_type="welcome",
            message_body="Welcome!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        sms3 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+3333333333",
            message_type="car_ready",
            message_body="Your car is ready!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        db.add_all([sms1, sms2, sms3])
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Filter by message_type
        response = client.get(
            "/api/sms-logs",
            params={"message_type": "welcome"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(log["message_type"] == "welcome" for log in data)
    
    def test_filter_sms_logs_by_status(self, client, db, test_staff, test_shop):
        """Test filtering SMS logs by status"""
        # Create SMS logs
        sms1 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+1111111111",
            message_type="welcome",
            message_body="Welcome!",
            status="sent",
            sent_at=datetime.utcnow()
        )
        sms2 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+2222222222",
            message_type="car_ready",
            message_body="Your car is ready!",
            status="delivered",
            sent_at=datetime.utcnow()
        )
        sms3 = SMSLogModel(
            shop_id=test_shop.id,
            recipient_phone="+3333333333",
            message_type="service_reminder",
            message_body="Time for service!",
            status="failed",
            error_message="Invalid phone number",
            sent_at=datetime.utcnow()
        )
        db.add_all([sms1, sms2, sms3])
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Filter by status
        response = client.get(
            "/api/sms-logs",
            params={"status": "failed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "failed"
        assert data[0]["error_message"] == "Invalid phone number"
    
    def test_sms_logs_pagination(self, client, db, test_staff, test_shop):
        """Test SMS logs pagination with skip and limit"""
        # Create multiple SMS logs
        for i in range(15):
            sms = SMSLogModel(
                shop_id=test_shop.id,
                recipient_phone=f"+111111{i:04d}",
                message_type="welcome",
                message_body=f"Welcome message {i}",
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(sms)
        db.commit()
        
        # Login as staff
        login_response = client.post(
            "/api/auth/staff/login",
            json={"username": "teststaff", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        
        # Get first page
        response = client.get(
            "/api/sms-logs",
            params={"skip": 0, "limit": 10},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 10
        
        # Get second page
        response = client.get(
            "/api/sms-logs",
            params={"skip": 10, "limit": 10},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5
