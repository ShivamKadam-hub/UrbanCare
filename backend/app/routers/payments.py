import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Payment, PaymentStatus, Booking, BookingStatus, User
from app.schemas.schemas import PaymentCreate, PaymentOut
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("", response_model=PaymentOut, status_code=201)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.customer_id != current_user.id:
        raise HTTPException(403, "Not your booking")

    existing = db.query(Payment).filter(Payment.booking_id == payload.booking_id).first()
    if existing:
        raise HTTPException(400, "Payment already exists for this booking")

    payment = Payment(
        booking_id=payload.booking_id,
        amount=payload.amount,
        method=payload.method,
        status=PaymentStatus.COMPLETED,
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
        paid_at=datetime.datetime.utcnow(),
    )
    db.add(payment)

    # auto-confirm booking on payment
    booking.status = BookingStatus.CONFIRMED
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=list[PaymentOut])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.models import ServiceProvider
    
    if current_user.role.value == "admin":
        return db.query(Payment).all()

    if current_user.role.value == "customer":
        # get payments for customer's bookings
        bookings = db.query(Booking).filter(Booking.customer_id == current_user.id).all()
        booking_ids = [b.id for b in bookings]
        return db.query(Payment).filter(Payment.booking_id.in_(booking_ids)).all()
    
    elif current_user.role.value == "provider":
        # get payments for provider's service bookings
        provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
        if not provider:
            return []
        service_ids = [s.id for s in provider.services]
        bookings = db.query(Booking).filter(Booking.service_id.in_(service_ids)).all()
        booking_ids = [b.id for b in bookings]
        return db.query(Payment).filter(Payment.booking_id.in_(booking_ids)).all()
    
    return []
