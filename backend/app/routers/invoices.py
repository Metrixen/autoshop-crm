from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Invoice, WorkOrder, WorkOrderLineItem, InvoiceStatus, Staff, Customer, UserRole
from app.schemas import Invoice as InvoiceSchema, InvoiceUpdate, InvoiceWithDetails
from app.utils.auth import get_current_staff, get_receptionist_or_higher, get_current_customer, get_current_user
from app.services.pdf import get_pdf_service, PDFService
from app.services.sms import get_sms_service, SMSService
from app.config import settings

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


def generate_invoice_number(shop_id: int, db: Session) -> str:
    """Generate sequential invoice number for shop"""
    # Get the last invoice for this shop
    last_invoice = db.query(Invoice).filter(
        Invoice.shop_id == shop_id
    ).order_by(Invoice.id.desc()).first()
    
    if last_invoice and last_invoice.invoice_number:
        # Extract number from last invoice (e.g., "INV-2024-00001")
        try:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    year = datetime.now().year
    return f"INV-{year}-{next_num:05d}"


@router.post("/from-work-order/{work_order_id}", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
def create_invoice_from_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Create invoice from work order when it's marked as done"""
    
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.shop_id == current_staff.shop_id
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Check if invoice already exists
    existing_invoice = db.query(Invoice).filter(Invoice.work_order_id == work_order_id).first()
    if existing_invoice:
        return existing_invoice
    
    # Calculate totals from line items
    line_items = db.query(WorkOrderLineItem).filter(
        WorkOrderLineItem.work_order_id == work_order_id
    ).all()
    
    subtotal = sum(item.total_price for item in line_items)
    tax_rate = 0.20  # 20% VAT for Bulgaria
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    # Create invoice
    invoice = Invoice(
        shop_id=work_order.shop_id,
        work_order_id=work_order.id,
        customer_id=work_order.customer_id,
        invoice_number=generate_invoice_number(work_order.shop_id, db),
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total=total,
        status=InvoiceStatus.DRAFT
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.get("", response_model=List[InvoiceSchema])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status_filter: InvoiceStatus = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List invoices"""
    
    if isinstance(current_user, Staff):
        query = db.query(Invoice).filter(Invoice.shop_id == current_user.shop_id)
    elif isinstance(current_user, Customer):
        query = db.query(Invoice).filter(
            Invoice.shop_id == current_user.shop_id,
            Invoice.customer_id == current_user.id
        )
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceWithDetails)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get invoice by ID"""
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Authorization
    if isinstance(current_user, Staff):
        if invoice.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif isinstance(current_user, Customer):
        if invoice.customer_id != current_user.id or invoice.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_receptionist_or_higher)
):
    """Update invoice (receptionist or higher)"""
    
    sms_service = get_sms_service(db)
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.shop_id == current_staff.shop_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Don't allow changes to finalized or paid invoices
    if invoice.status in [InvoiceStatus.FINALIZED, InvoiceStatus.PAID] and update_data.status != InvoiceStatus.PAID:
        raise HTTPException(status_code=400, detail="Cannot modify finalized or paid invoices")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(invoice, field, value)
    
    # Handle status changes
    if update_data.status == InvoiceStatus.FINALIZED and invoice.status == InvoiceStatus.DRAFT:
        invoice.finalized_at = datetime.utcnow()
        invoice.finalized_by_staff_id = current_staff.id
    
    if update_data.status == InvoiceStatus.PAID and invoice.status != InvoiceStatus.PAID:
        invoice.paid_at = datetime.utcnow()
        
        # Send car ready SMS to customer
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        work_order = db.query(WorkOrder).filter(WorkOrder.id == invoice.work_order_id).first()
        if customer and work_order:
            from app.models import Car
            car = db.query(Car).filter(Car.id == work_order.car_id).first()
            if car:
                car_info = f"{car.make} {car.model} ({car.license_plate})"
                customer_name = f"{customer.first_name} {customer.last_name}"
                sms_service.send_car_ready_sms(
                    shop_id=invoice.shop_id,
                    customer_phone=customer.phone,
                    customer_name=customer_name,
                    car_info=car_info,
                    total=invoice.total,
                    shop_website=settings.SHOP_WEBSITE
                )
    
    invoice.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Download invoice as PDF"""
    
    pdf_service = get_pdf_service()
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Authorization
    if isinstance(current_user, Staff):
        if invoice.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif isinstance(current_user, Customer):
        if invoice.customer_id != current_user.id or invoice.shop_id != current_user.shop_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get related data
    work_order = db.query(WorkOrder).filter(WorkOrder.id == invoice.work_order_id).first()
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    line_items = db.query(WorkOrderLineItem).filter(
        WorkOrderLineItem.work_order_id == invoice.work_order_id
    ).all()
    
    from app.models import Shop
    shop = db.query(Shop).filter(Shop.id == invoice.shop_id).first()
    
    # Prepare data for PDF
    invoice_data = {
        "invoice_number": invoice.invoice_number,
        "created_at": invoice.created_at,
        "subtotal": invoice.subtotal,
        "tax_rate": invoice.tax_rate,
        "tax_amount": invoice.tax_amount,
        "total": invoice.total,
        "notes": invoice.notes,
        "status": invoice.status.value,
        "paid_at": invoice.paid_at,
        "payment_method": invoice.payment_method
    }
    
    work_order_data = {
        "reported_issues": work_order.reported_issues,
        "mileage_at_intake": work_order.mileage_at_intake
    }
    
    shop_data = {
        "name": shop.name,
        "address": shop.address,
        "phone": shop.phone,
        "email": shop.email,
        "website": shop.website
    }
    
    customer_data = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "email": customer.email
    }
    
    line_items_data = [
        {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        }
        for item in line_items
    ]
    
    # Generate PDF
    pdf_path = pdf_service.generate_invoice_pdf(
        invoice_data, work_order_data, shop_data, customer_data, line_items_data
    )
    
    # Update invoice with PDF URL
    if not invoice.pdf_url:
        invoice.pdf_url = pdf_path
        db.commit()
    
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{invoice.invoice_number}.pdf")
