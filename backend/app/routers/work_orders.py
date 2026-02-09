from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import WorkOrder, WorkOrderLineItem, WorkOrderAssignmentHistory, Staff, Customer, Car, UserRole, WorkOrderStatus
from app.schemas import (WorkOrder as WorkOrderSchema, WorkOrderCreate, WorkOrderUpdate, 
                          WorkOrderWithDetails, WorkOrderLineItemCreate, WorkOrderLineItem as WorkOrderLineItemSchema,
                          WorkOrderReassign)
from app.utils.auth import get_current_staff, get_receptionist_or_higher, get_current_user
from app.services.mileage import get_mileage_service, MileageService

router = APIRouter(prefix="/api/work-orders", tags=["Work Orders"])


@router.post("/", response_model=WorkOrderSchema, status_code=status.HTTP_201_CREATED)
def create_work_order(
    work_order_data: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Create a new work order (receptionist or higher)"""
    
    # Verify customer and car exist and belong to the shop
    customer = db.query(Customer).filter(
        Customer.id == work_order_data.customer_id,
        Customer.shop_id == work_order_data.shop_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    car = db.query(Car).filter(
        Car.id == work_order_data.car_id,
        Car.shop_id == work_order_data.shop_id
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Verify assigned mechanic if provided
    if work_order_data.assigned_mechanic_id:
        mechanic = db.query(Staff).filter(
            Staff.id == work_order_data.assigned_mechanic_id,
            Staff.shop_id == work_order_data.shop_id,
            Staff.role.in_([UserRole.MECHANIC, UserRole.MANAGER, UserRole.SUPER_ADMIN])
        ).first()
        
        if not mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
    
    work_order = WorkOrder(**work_order_data.dict())
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    
    return work_order


@router.get("/", response_model=List[WorkOrderWithDetails])
def list_work_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: WorkOrderStatus = None,
    assigned_mechanic_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List work orders"""
    
    if isinstance(current_user, Staff):
        query = db.query(WorkOrder).filter(WorkOrder.shop_id == current_user.shop_id)
        
        # Mechanics only see their assigned work orders unless they're managers
        if current_user.role == UserRole.MECHANIC:
            query = query.filter(WorkOrder.assigned_mechanic_id == current_user.id)
        
    elif isinstance(current_user, Customer):
        # Customers only see their own work orders
        query = db.query(WorkOrder).filter(
            WorkOrder.shop_id == current_user.shop_id,
            WorkOrder.customer_id == current_user.id
        )
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    
    if assigned_mechanic_id:
        query = query.filter(WorkOrder.assigned_mechanic_id == assigned_mechanic_id)
    
    work_orders = query.order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()
    return work_orders


@router.get("/my-tasks", response_model=List[WorkOrderWithDetails])
def get_my_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get work orders assigned to current mechanic"""
    
    work_orders = db.query(WorkOrder).filter(
        WorkOrder.shop_id == current_staff.shop_id,
        WorkOrder.assigned_mechanic_id == current_staff.id,
        WorkOrder.status != WorkOrderStatus.DONE
    ).order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()
    
    return work_orders


@router.get("/{work_order_id}", response_model=WorkOrderWithDetails)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get work order by ID"""
    
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Authorization check
    if isinstance(current_user, Staff):
        if work_order.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Mechanics can only see their own work orders
        if current_user.role == UserRole.MECHANIC and work_order.assigned_mechanic_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    elif isinstance(current_user, Customer):
        if work_order.customer_id != current_user.id or work_order.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return work_order


@router.put("/{work_order_id}", response_model=WorkOrderSchema)
def update_work_order(
    work_order_id: int,
    update_data: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Update work order"""
    
    mileage_service = get_mileage_service(db)
    
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.shop_id == current_staff.shop_id
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Authorization: mechanics can only update their own work orders
    if current_staff.role == UserRole.MECHANIC and work_order.assigned_mechanic_id != current_staff.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(work_order, field, value)
    
    # Handle status changes
    if update_data.status:
        if update_data.status == WorkOrderStatus.IN_PROGRESS and not work_order.started_at:
            work_order.started_at = datetime.utcnow()
        elif update_data.status == WorkOrderStatus.DONE and not work_order.completed_at:
            work_order.completed_at = datetime.utcnow()
            
            # Update car mileage if work order has mileage
            if work_order.mileage_at_intake:
                mileage_service.update_car_mileage(work_order.car_id, work_order.mileage_at_intake)
    
    work_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(work_order)
    
    return work_order


@router.post("/{work_order_id}/reassign", response_model=WorkOrderSchema)
def reassign_work_order(
    work_order_id: int,
    reassign_data: WorkOrderReassign,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Reassign work order to another mechanic"""
    
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.shop_id == current_staff.shop_id
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Verify new mechanic exists
    new_mechanic = db.query(Staff).filter(
        Staff.id == reassign_data.new_mechanic_id,
        Staff.shop_id == current_staff.shop_id,
        Staff.role.in_([UserRole.MECHANIC, UserRole.MANAGER])
    ).first()
    
    if not new_mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
    # Log reassignment
    history = WorkOrderAssignmentHistory(
        work_order_id=work_order.id,
        previous_mechanic_id=work_order.assigned_mechanic_id,
        new_mechanic_id=reassign_data.new_mechanic_id,
        reassigned_by_staff_id=current_staff.id,
        reason=reassign_data.reason
    )
    db.add(history)
    
    # Update assignment
    work_order.assigned_mechanic_id = reassign_data.new_mechanic_id
    work_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(work_order)
    
    return work_order


@router.post("/{work_order_id}/line-items", response_model=WorkOrderLineItemSchema)
def add_line_item(
    work_order_id: int,
    line_item_data: WorkOrderLineItemCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Add line item to work order"""
    
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.shop_id == current_staff.shop_id
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Calculate total price
    total_price = line_item_data.quantity * line_item_data.unit_price
    
    line_item = WorkOrderLineItem(
        work_order_id=work_order_id,
        item_type=line_item_data.item_type,
        description=line_item_data.description,
        quantity=line_item_data.quantity,
        unit_price=line_item_data.unit_price,
        total_price=total_price,
        added_by_staff_id=current_staff.id
    )
    
    db.add(line_item)
    db.commit()
    db.refresh(line_item)
    
    return line_item


@router.delete("/{work_order_id}/line-items/{line_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_line_item(
    work_order_id: int,
    line_item_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Delete line item from work order"""
    
    line_item = db.query(WorkOrderLineItem).filter(
        WorkOrderLineItem.id == line_item_id,
        WorkOrderLineItem.work_order_id == work_order_id
    ).first()
    
    if not line_item:
        raise HTTPException(status_code=404, detail="Line item not found")
    
    # Verify work order belongs to staff's shop
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.shop_id == current_staff.shop_id
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(line_item)
    db.commit()
    return None
