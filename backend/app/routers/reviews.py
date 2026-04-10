from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Review, Booking, BookingStatus, User
from app.schemas.schemas import ReviewCreate, ReviewOut, ReviewDetail
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOut, status_code=201)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer")),
):
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.customer_id != current_user.id:
        raise HTTPException(403, "Not your booking")
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(400, "Can only review completed bookings")

    existing = db.query(Review).filter(Review.booking_id == payload.booking_id).first()
    if existing:
        raise HTTPException(400, "Review already submitted for this booking")

    if not (1 <= payload.rating <= 5):
        raise HTTPException(400, "Rating must be between 1 and 5")

    review = Review(
        booking_id=payload.booking_id,
        customer_id=current_user.id,
        service_id=booking.service_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/service/{service_id}", response_model=list[ReviewDetail])
def get_service_reviews(service_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .options(joinedload(Review.customer))
        .filter(Review.service_id == service_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return reviews
