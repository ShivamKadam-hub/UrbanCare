from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.models import (
    User, UserRole, ServiceProvider, Category, Service, Booking, Payment, PaymentStatus,
)
from app.schemas.schemas import (
    UserOut, ProviderDetail, CategoryCreate, CategoryOut, AnalyticsOut, BookingDetail, BookingOut,
)
from app.utils.auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin"])

admin_only = require_role("admin")


# ── Users ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
def list_users(
    role: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    return q.offset(skip).limit(limit).all()


@router.patch("/users/{user_id}/toggle", response_model=UserOut)
def toggle_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


# ── Providers ────────────────────────────────────────────────────────────────

@router.get("/providers", response_model=list[ProviderDetail])
def list_providers(
    approved: bool = None,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    q = db.query(ServiceProvider)
    if approved is not None:
        q = q.filter(ServiceProvider.is_approved == approved)
    return q.all()


@router.patch("/providers/{provider_id}/approve", response_model=ProviderDetail)
def approve_provider(provider_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(404, "Provider not found")
    provider.is_approved = True
    db.commit()
    db.refresh(provider)
    return provider


# ── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    try:
        return db.query(Category).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    for k, v in payload.model_dump().items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    db.delete(cat)
    db.commit()


# ── Bookings ─────────────────────────────────────────────────────────────────

@router.get("/bookings", response_model=list[BookingOut])
def list_all_bookings(
    status: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    q = db.query(Booking)
    if status:
        q = q.filter(Booking.status == status)
    return q.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()


# ── Analytics ────────────────────────────────────────────────────────────────

@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    total_users = db.query(func.count(User.id)).scalar()
    total_providers = db.query(func.count(ServiceProvider.id)).scalar()
    total_services = db.query(func.count(Service.id)).scalar()
    total_bookings = db.query(func.count(Booking.id)).scalar()
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.status == PaymentStatus.COMPLETED).scalar()
    pending_approvals = db.query(func.count(ServiceProvider.id)).filter(ServiceProvider.is_approved == False).scalar()

    # bookings by status
    status_counts = db.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    bookings_by_status = {s.value if hasattr(s, "value") else s: c for s, c in status_counts}

    return AnalyticsOut(
        total_users=total_users,
        total_providers=total_providers,
        total_services=total_services,
        total_bookings=total_bookings,
        total_revenue=float(total_revenue),
        pending_approvals=pending_approvals,
        bookings_by_status=bookings_by_status,
    )
