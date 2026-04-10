from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import uuid
import datetime

from app.database import get_db
from app.models.models import Booking, BookingStatus, Service, ServiceProvider, User, Payment, PaymentStatus
from app.schemas.schemas import BookingCreate, BookingStatusUpdate, BookingOut, BookingDetail
from app.utils.auth import get_current_user, require_role
from app.utils.email import send_booking_confirmation

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer")),
):
    service = db.query(Service).filter(Service.id == payload.service_id, Service.is_active == True).first()
    if not service:
        raise HTTPException(404, "Service not found or inactive")

    booking = Booking(customer_id=current_user.id, **payload.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("", response_model=list[BookingDetail])
def list_bookings(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Booking).options(joinedload(Booking.service), joinedload(Booking.customer))

    if current_user.role.value == "customer":
        q = q.filter(Booking.customer_id == current_user.id)
    elif current_user.role.value == "provider":
        provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
        if provider:
            service_ids = [s.id for s in provider.services]
            q = q.filter(Booking.service_id.in_(service_ids))
        else:
            return []
    # admin sees all

    if status:
        q = q.filter(Booking.status == status)

    return q.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{booking_id}", response_model=BookingDetail)
def get_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.service), joinedload(Booking.customer))
        .filter(Booking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking


@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")

    try:
        new_status = BookingStatus(payload.status)
    except ValueError:
        raise HTTPException(400, f"Invalid status: {payload.status}")

    booking.status = new_status
    
    # Auto-create payment when booking is marked as completed
    if new_status == BookingStatus.COMPLETED:
        existing_payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
        if not existing_payment:
            service = db.query(Service).filter(Service.id == booking.service_id).first()
            if service:
                payment = Payment(
                    booking_id=booking.id,
                    amount=service.price,
                    method="card",
                    status=PaymentStatus.COMPLETED,
                    transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                    paid_at=datetime.datetime.utcnow(),
                )
                db.add(payment)
    
    db.commit()
    db.refresh(booking)

    # send email on confirmation
    if new_status == BookingStatus.CONFIRMED:
        customer = db.query(User).filter(User.id == booking.customer_id).first()
        service = db.query(Service).filter(Service.id == booking.service_id).first()
        if customer and service:
            send_booking_confirmation(customer.email, booking.id, service.title, booking.booking_date, booking.time_slot)

    return booking
