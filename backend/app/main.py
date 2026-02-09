from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.services.scheduler import scheduler_service

# Import routers
from app.routers import (
    auth,
    customers,
    cars,
    work_orders,
    invoices,
    appointments,
    shop,
    staff,
    admin,
    reports
)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="White-label CRM SaaS for auto repair shops",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(cars.router)
app.include_router(work_orders.router)
app.include_router(invoices.router)
app.include_router(appointments.router)
app.include_router(shop.router)
app.include_router(staff.router)
app.include_router(admin.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler"""
    init_db()
    scheduler_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown background scheduler"""
    scheduler_service.shutdown()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AutoShop CRM API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2026-02-09T12:53:29.087Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
