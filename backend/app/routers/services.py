from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.database import get_db
from app.models.models import Service, ServiceProvider, User
from app.schemas.schemas import ServiceCreate, ServiceUpdate, ServiceOut, ServiceDetail
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Service).filter(Service.is_active == True)
        if category_id:
            q = q.filter(Service.category_id == category_id)
        if search:
            q = q.filter(Service.title.ilike(f"%{search}%"))
        if min_price is not None:
            q = q.filter(Service.price >= min_price)
        if max_price is not None:
            q = q.filter(Service.price <= max_price)
        return q.offset(skip).limit(limit).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/{service_id}", response_model=ServiceDetail)
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = (
        db.query(Service)
        .options(joinedload(Service.provider), joinedload(Service.category))
        .filter(Service.id == service_id)
        .first()
    )
    if not svc:
        raise HTTPException(404, "Service not found")
    return svc


@router.post("", response_model=ServiceOut, status_code=201)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(400, "Provider profile not found")
    if not provider.is_approved:
        raise HTTPException(403, "Provider not yet approved by admin")

    svc = Service(provider_id=provider.id, **payload.model_dump())
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    svc = db.query(Service).filter(Service.id == service_id, Service.provider_id == provider.id).first()
    if not svc:
        raise HTTPException(404, "Service not found or access denied")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(svc, field, value)
    db.commit()
    db.refresh(svc)
    return svc


@router.delete("/{service_id}", status_code=204)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("provider")),
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    svc = db.query(Service).filter(Service.id == service_id, Service.provider_id == provider.id).first()
    if not svc:
        raise HTTPException(404, "Service not found or access denied")
    db.delete(svc)
    db.commit()
