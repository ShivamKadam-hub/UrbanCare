"""
Reminders API Router
Endpoints for managing recurring services and reminders
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.models import (
    RecurringService, Reminder, Service, User, ReminderStatus,
    RecurrenceType
)
from app.schemas.schemas import (
    RecurringServiceCreate, RecurringServiceUpdate, RecurringServiceOut,
    RecurringServiceDetail, ReminderCreate, ReminderOut, ReminderMarkRead
)
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/recurring-services", tags=["Recurring Services & Reminders"])


# ────────────────────────────────────────────────────────────────────────────
# RECURRING SERVICES ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=RecurringServiceOut, status_code=201)
def create_recurring_service(
    payload: RecurringServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("customer")),
):
    """Create a new recurring service"""
    # Validate service exists
    service = db.query(Service).filter(
        Service.id == payload.service_id,
        Service.is_active == True
    ).first()
    if not service:
        raise HTTPException(404, "Service not found or inactive")
    
    # Create recurring service
    recurring = RecurringService(
        customer_id=current_user.id,
        service_id=payload.service_id,
        recurrence_type=payload.recurrence_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        next_booking_date=payload.start_date,
        notes=payload.notes
    )
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring


@router.get("", response_model=list[RecurringServiceOut])
def list_recurring_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recurring services (only own, or all if admin)"""
    q = db.query(RecurringService)
    
    if current_user.role.value != "admin":
        q = q.filter(RecurringService.customer_id == current_user.id)
    
    return q.order_by(RecurringService.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{recurring_id}", response_model=RecurringServiceDetail)
def get_recurring_service(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific recurring service"""
    recurring = db.query(RecurringService).filter(
        RecurringService.id == recurring_id
    ).first()
    
    if not recurring:
        raise HTTPException(404, "Recurring service not found")
    
    # Check authorization
    if current_user.role.value == "customer" and recurring.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to view this recurring service")
    
    return recurring


@router.patch("/{recurring_id}", response_model=RecurringServiceOut)
def update_recurring_service(
    recurring_id: int,
    payload: RecurringServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a recurring service"""
    recurring = db.query(RecurringService).filter(
        RecurringService.id == recurring_id
    ).first()
    
    if not recurring:
        raise HTTPException(404, "Recurring service not found")
    
    # Check authorization
    if current_user.role.value == "customer" and recurring.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to update this recurring service")
    
    # Update fields
    if payload.recurrence_type:
        recurring.recurrence_type = payload.recurrence_type
    if payload.end_date is not None:
        recurring.end_date = payload.end_date
    if payload.is_active is not None:
        recurring.is_active = payload.is_active
    if payload.notes is not None:
        recurring.notes = payload.notes
    
    db.commit()
    db.refresh(recurring)
    return recurring


@router.delete("/{recurring_id}", status_code=204)
def delete_recurring_service(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a recurring service (soft delete)"""
    recurring = db.query(RecurringService).filter(
        RecurringService.id == recurring_id
    ).first()
    
    if not recurring:
        raise HTTPException(404, "Recurring service not found")
    
    # Check authorization
    if current_user.role.value == "customer" and recurring.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this recurring service")
    
    # Soft delete
    recurring.is_active = False
    db.commit()
    return None


# ────────────────────────────────────────────────────────────────────────────
# REMINDERS ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.get("/reminders/all", response_model=list[ReminderOut])
def list_reminders(
    status: Optional[str] = None,
    reminder_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List reminders for current user"""
    q = db.query(Reminder)
    
    if current_user.role.value == "customer":
        q = q.filter(Reminder.customer_id == current_user.id)
    elif current_user.role.value == "provider":
        from app.models.models import ServiceProvider
        provider = db.query(ServiceProvider).filter(
            ServiceProvider.user_id == current_user.id
        ).first()
        if provider:
            q = q.filter(Reminder.provider_id == provider.id)
        else:
            return []
    # Admin sees all
    
    if status:
        q = q.filter(Reminder.reminder_status == status)
    
    if reminder_type:
        q = q.filter(Reminder.reminder_type == reminder_type)
    
    return q.order_by(Reminder.scheduled_date.asc()).offset(skip).limit(limit).all()


@router.get("/{recurring_id}/reminders", response_model=list[ReminderOut])
def list_reminders_for_service(
    recurring_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List reminders for a specific recurring service"""
    recurring = db.query(RecurringService).filter(
        RecurringService.id == recurring_id
    ).first()
    
    if not recurring:
        raise HTTPException(404, "Recurring service not found")
    
    # Check authorization
    if current_user.role.value == "customer" and recurring.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to view these reminders")
    
    reminders = db.query(Reminder).filter(
        Reminder.recurring_service_id == recurring_id
    ).order_by(Reminder.scheduled_date.asc()).offset(skip).limit(limit).all()
    
    return reminders


@router.get("/reminders/{reminder_id}", response_model=ReminderOut)
def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    
    # Check authorization
    if current_user.role.value == "customer" and reminder.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to view this reminder")
    
    return reminder


@router.patch("/reminders/{reminder_id}/read", response_model=ReminderOut)
def mark_reminder_read(
    reminder_id: int,
    payload: ReminderMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a reminder as read/unread (for in-app reminders)"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    
    # Check authorization
    if current_user.role.value == "customer" and reminder.customer_id != current_user.id:
        raise HTTPException(403, "Not authorized to update this reminder")
    
    reminder.is_read = payload.is_read
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/stats/upcoming", response_model=dict)
def get_upcoming_reminders_stats(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get stats on upcoming reminders"""
    now = datetime.utcnow()
    future_date = now + timedelta(days=days)
    
    q = db.query(Reminder).filter(
        Reminder.scheduled_date.between(now, future_date),
        Reminder.reminder_status == ReminderStatus.PENDING,
    )
    
    if current_user.role.value == "customer":
        q = q.filter(Reminder.customer_id == current_user.id)
    
    reminders = q.all()
    
    return {
        "total_upcoming": len(reminders),
        "by_type": {
            "email": len([r for r in reminders if r.reminder_type == "email"]),
            "in_app": len([r for r in reminders if r.reminder_type == "in_app"]),
            "sms": len([r for r in reminders if r.reminder_type == "sms"]),
        },
        "date_range": {
            "from": now.isoformat(),
            "to": future_date.isoformat(),
        }
    }
