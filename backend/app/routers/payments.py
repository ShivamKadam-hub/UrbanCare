import uuid
import datetime
import stripe
from stripe._error import StripeError, SignatureVerificationError
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.models import Payment, PaymentStatus, Booking, BookingStatus, Service, User
from app.schemas.schemas import (
    PaymentCreate, PaymentOut,
    CheckoutSessionCreate, CheckoutSessionResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ── Stripe Checkout Session ──────────────────────────────────────────────────

@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe Checkout Session for a booking."""
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.customer_id != current_user.id:
        raise HTTPException(403, "Not your booking")

    # Check for existing payment
    existing = db.query(Payment).filter(Payment.booking_id == payload.booking_id).first()
    if existing and existing.status == PaymentStatus.COMPLETED:
        raise HTTPException(400, "Payment already completed for this booking")

    # Get service details for the line item
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(404, "Service not found")

    # Build base URL for success/cancel redirects
    origin = request.headers.get("origin", "http://localhost:5173")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": service.title,
                        "description": f"Booking #{booking.id} — {service.title} on {booking.booking_date} at {booking.time_slot}",
                    },
                    "unit_amount": int(service.price * 100),  # Stripe uses paise/cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{origin}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&booking_id={booking.id}",
            cancel_url=f"{origin}/payment/cancel?booking_id={booking.id}",
            metadata={
                "booking_id": str(booking.id),
                "customer_id": str(current_user.id),
                "service_title": service.title,
            },
            customer_email=current_user.email,
        )
    except StripeError as e:
        raise HTTPException(500, f"Stripe error: {str(e)}")

    # Create or update a pending Payment record
    if existing:
        existing.stripe_session_id = checkout_session.id
        existing.status = PaymentStatus.PENDING
    else:
        payment = Payment(
            booking_id=booking.id,
            amount=service.price,
            method="card",
            status=PaymentStatus.PENDING,
            stripe_session_id=checkout_session.id,
        )
        db.add(payment)

    db.commit()

    return CheckoutSessionResponse(
        session_id=checkout_session.id,
        checkout_url=checkout_session.url,
        publishable_key=settings.STRIPE_PUBLISHABLE_KEY,
    )


# ── Stripe Webhook ───────────────────────────────────────────────────────────

@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events — especially checkout.session.completed."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify webhook signature
    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            # For local dev without webhook secret, parse raw payload
            import json
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _handle_checkout_completed(session, db)
    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        _handle_checkout_expired(session, db)

    return {"status": "ok"}


def _get_session_field(session, field):
    """Get a field from a Stripe session object or dict (handles both Stripe v15 objects and webhook dicts)."""
    try:
        return getattr(session, field)
    except (AttributeError, KeyError):
        pass
    try:
        return session[field]
    except (KeyError, TypeError):
        pass
    try:
        return session.get(field)
    except AttributeError:
        return None


def _handle_checkout_completed(session, db: Session):
    """Mark payment as completed and confirm the booking."""
    session_id = _get_session_field(session, "id")
    payment_intent_id = _get_session_field(session, "payment_intent")

    payment = db.query(Payment).filter(Payment.stripe_session_id == session_id).first()
    if not payment:
        return  # Unknown session, skip

    payment.status = PaymentStatus.COMPLETED
    payment.stripe_payment_intent_id = payment_intent_id
    payment.transaction_id = payment_intent_id or f"TXN-{uuid.uuid4().hex[:12].upper()}"
    payment.paid_at = datetime.datetime.utcnow()

    # Auto-confirm booking
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking:
        booking.status = BookingStatus.CONFIRMED

    db.commit()


def _handle_checkout_expired(session, db: Session):
    """Mark payment as failed when checkout session expires."""
    session_id = _get_session_field(session, "id")
    payment = db.query(Payment).filter(Payment.stripe_session_id == session_id).first()
    if payment and payment.status == PaymentStatus.PENDING:
        payment.status = PaymentStatus.FAILED
        db.commit()


# ── Verify Payment ───────────────────────────────────────────────────────────

@router.get("/verify/{session_id}")
def verify_payment(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a payment by checking its Stripe session status."""
    payment = db.query(Payment).filter(Payment.stripe_session_id == session_id).first()

    if not payment:
        raise HTTPException(404, "Payment not found")

    # Verify ownership
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking and booking.customer_id != current_user.id:
        raise HTTPException(403, "Not your payment")

    # If still pending, check with Stripe directly
    if payment.status == PaymentStatus.PENDING:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                _handle_checkout_completed(session, db)
                db.refresh(payment)
        except StripeError:
            pass

    service = db.query(Service).filter(Service.id == booking.service_id).first() if booking else None

    return {
        "payment_status": payment.status.value,
        "booking_id": payment.booking_id,
        "amount": payment.amount,
        "transaction_id": payment.transaction_id,
        "service_title": service.title if service else "Unknown Service",
        "booking_date": booking.booking_date if booking else None,
        "time_slot": booking.time_slot if booking else None,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
    }


# ── Legacy Payment (cash / fallback) ────────────────────────────────────────

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


# ── List Payments ────────────────────────────────────────────────────────────

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


# ── Stripe Config (public) ──────────────────────────────────────────────────

@router.get("/config")
def get_stripe_config():
    """Return the publishable key so the frontend can initialise Stripe.js."""
    return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}
