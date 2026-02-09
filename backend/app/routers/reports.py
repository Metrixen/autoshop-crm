from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import (Shop, Staff, Customer, WorkOrder, Invoice, Appointment, 
                        WorkOrderStatus, InvoiceStatus, AppointmentStatus, UserRole, WorkOrderLineItem)
from app.schemas import DashboardStats, MechanicPerformance, RevenueBreakdown, PopularService
from app.utils.auth import get_current_staff, get_manager

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get dashboard statistics"""
    
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Total customers
    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.shop_id == current_staff.shop_id,
        Customer.is_active == True
    ).scalar()
    
    # Active work orders
    active_work_orders = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.shop_id == current_staff.shop_id,
        WorkOrder.status != WorkOrderStatus.DONE
    ).scalar()
    
    # Completed work orders today
    completed_today = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.shop_id == current_staff.shop_id,
        WorkOrder.status == WorkOrderStatus.DONE,
        func.date(WorkOrder.completed_at) == today
    ).scalar()
    
    # Revenue today
    revenue_today = db.query(func.sum(Invoice.total)).filter(
        Invoice.shop_id == current_staff.shop_id,
        Invoice.status == InvoiceStatus.PAID,
        func.date(Invoice.paid_at) == today
    ).scalar() or 0.0
    
    # Revenue this week
    revenue_week = db.query(func.sum(Invoice.total)).filter(
        Invoice.shop_id == current_staff.shop_id,
        Invoice.status == InvoiceStatus.PAID,
        func.date(Invoice.paid_at) >= week_start
    ).scalar() or 0.0
    
    # Revenue this month
    revenue_month = db.query(func.sum(Invoice.total)).filter(
        Invoice.shop_id == current_staff.shop_id,
        Invoice.status == InvoiceStatus.PAID,
        func.date(Invoice.paid_at) >= month_start
    ).scalar() or 0.0
    
    # Pending appointments
    pending_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.shop_id == current_staff.shop_id,
        Appointment.status == AppointmentStatus.REQUESTED
    ).scalar()
    
    return DashboardStats(
        total_customers=total_customers,
        active_work_orders=active_work_orders,
        completed_work_orders_today=completed_today,
        revenue_today=revenue_today,
        revenue_week=revenue_week,
        revenue_month=revenue_month,
        pending_appointments=pending_appointments
    )


@router.get("/mechanics-performance", response_model=List[MechanicPerformance])
def get_mechanics_performance(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Get mechanic performance metrics (manager or super admin only)"""
    
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all mechanics
    mechanics = db.query(Staff).filter(
        Staff.shop_id == current_staff.shop_id,
        Staff.role == UserRole.MECHANIC,
        Staff.is_active == True
    ).all()
    
    performance_data = []
    
    for mechanic in mechanics:
        # Get completed work orders
        completed_work_orders = db.query(WorkOrder).filter(
            WorkOrder.shop_id == current_staff.shop_id,
            WorkOrder.assigned_mechanic_id == mechanic.id,
            WorkOrder.status == WorkOrderStatus.DONE,
            WorkOrder.completed_at >= start_date,
            WorkOrder.completed_at <= end_date
        ).all()
        
        if not completed_work_orders:
            continue
        
        # Calculate average completion time
        completion_times = []
        for wo in completed_work_orders:
            if wo.started_at and wo.completed_at:
                time_diff = (wo.completed_at - wo.started_at).total_seconds() / 3600  # hours
                completion_times.append(time_diff)
        
        avg_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Calculate total revenue from mechanic's work orders
        work_order_ids = [wo.id for wo in completed_work_orders]
        total_revenue = db.query(func.sum(Invoice.total)).filter(
            Invoice.work_order_id.in_(work_order_ids),
            Invoice.status == InvoiceStatus.PAID
        ).scalar() or 0.0
        
        performance_data.append(MechanicPerformance(
            mechanic_id=mechanic.id,
            mechanic_name=f"{mechanic.first_name} {mechanic.last_name}",
            completed_work_orders=len(completed_work_orders),
            average_completion_time_hours=round(avg_time, 2),
            total_revenue=total_revenue
        ))
    
    return performance_data


@router.get("/revenue-breakdown", response_model=List[RevenueBreakdown])
def get_revenue_breakdown(
    period: str = "daily",  # daily, weekly, monthly
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Get revenue breakdown over time (manager or super admin only)"""
    
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query invoices
    invoices = db.query(Invoice).filter(
        Invoice.shop_id == current_staff.shop_id,
        Invoice.status == InvoiceStatus.PAID,
        Invoice.paid_at >= start_date,
        Invoice.paid_at <= end_date
    ).all()
    
    # Group by date
    revenue_by_date = {}
    for invoice in invoices:
        if period == "daily":
            date_key = invoice.paid_at.strftime("%Y-%m-%d")
        elif period == "weekly":
            date_key = invoice.paid_at.strftime("%Y-W%W")
        else:  # monthly
            date_key = invoice.paid_at.strftime("%Y-%m")
        
        if date_key not in revenue_by_date:
            revenue_by_date[date_key] = {"revenue": 0.0, "count": 0}
        
        revenue_by_date[date_key]["revenue"] += invoice.total
        revenue_by_date[date_key]["count"] += 1
    
    breakdown = [
        RevenueBreakdown(
            date=date_key,
            revenue=data["revenue"],
            work_orders_count=data["count"]
        )
        for date_key, data in sorted(revenue_by_date.items())
    ]
    
    return breakdown


@router.get("/popular-services", response_model=List[PopularService])
def get_popular_services(
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_manager)
):
    """Get most popular services (manager or super admin only)"""
    
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get work orders in date range
    work_orders = db.query(WorkOrder).filter(
        WorkOrder.shop_id == current_staff.shop_id,
        WorkOrder.status == WorkOrderStatus.DONE,
        WorkOrder.completed_at >= start_date,
        WorkOrder.completed_at <= end_date
    ).all()
    
    work_order_ids = [wo.id for wo in work_orders]
    
    if not work_order_ids:
        return []
    
    # Query line items and group by description
    line_items_query = db.query(
        WorkOrderLineItem.description,
        func.count(WorkOrderLineItem.id).label("count"),
        func.sum(WorkOrderLineItem.total_price).label("total_revenue")
    ).filter(
        WorkOrderLineItem.work_order_id.in_(work_order_ids)
    ).group_by(
        WorkOrderLineItem.description
    ).order_by(
        func.count(WorkOrderLineItem.id).desc()
    ).limit(limit)
    
    results = line_items_query.all()
    
    popular_services = [
        PopularService(
            service_name=result[0],
            count=result[1],
            total_revenue=result[2] or 0.0
        )
        for result in results
    ]
    
    return popular_services
