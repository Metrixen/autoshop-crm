from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "AutoShop CRM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./autoshop.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    SMS_ENABLED: bool = False
    
    # Stripe Payments
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Shop Configuration
    SHOP_NAME: str = "Demo Auto Shop"
    SHOP_PHONE: str = "+359888123456"
    SHOP_ADDRESS: str = "Sofia, Bulgaria"
    SHOP_WEBSITE: str = "https://example.com"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Mileage Prediction
    MIN_VISITS_FOR_PREDICTION: int = 2
    SERVICE_REMINDER_DAYS_AHEAD: int = 14
    
    # Background Jobs
    ENABLE_SCHEDULER: bool = True
    MILEAGE_CHECK_HOUR: int = 9  # Run at 9 AM daily
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
