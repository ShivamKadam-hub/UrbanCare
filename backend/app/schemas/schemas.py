from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str = "customer"  # customer | provider
    # provider-specific
    business_name: Optional[str] = None
    experience_years: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Category ─────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ── Service Provider ─────────────────────────────────────────────────────────

class ProviderOut(BaseModel):
    id: int
    user_id: int
    business_name: str
    description: Optional[str] = None
    experience_years: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderDetail(ProviderOut):
    user: UserOut


# ── Service ──────────────────────────────────────────────────────────────────

class ServiceCreate(BaseModel):
    category_id: int
    title: str
    description: Optional[str] = None
    price: float
    duration_minutes: int = 60
    image_url: Optional[str] = None


class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceOut(BaseModel):
    id: int
    provider_id: int
    category_id: int
    title: str
    description: Optional[str] = None
    price: float
    duration_minutes: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceDetail(ServiceOut):
    provider: ProviderOut
    category: CategoryOut


# ── Booking ──────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    service_id: int
    booking_date: str   # YYYY-MM-DD
    time_slot: str      # "10:00-11:00"
    address: str
    notes: Optional[str] = None


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed | rejected | completed | cancelled


class BookingOut(BaseModel):
    id: int
    customer_id: int
    service_id: int
    booking_date: str
    time_slot: str
    address: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingDetail(BookingOut):
    service: ServiceOut
    customer: UserOut


# ── Payment ──────────────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    method: str = "card"


class CheckoutSessionCreate(BaseModel):
    booking_id: int


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str
    publishable_key: str


class PaymentOut(BaseModel):
    id: int
    booking_id: int
    amount: float
    method: str
    status: str
    transaction_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Review ───────────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int  # 1-5
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    service_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewDetail(ReviewOut):
    customer: UserOut


# ── Recurring Services ───────────────────────────────────────────────────────

class RecurringServiceCreate(BaseModel):
    service_id: int
    recurrence_type: str  # weekly, biweekly, monthly
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class RecurringServiceUpdate(BaseModel):
    recurrence_type: Optional[str] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class RecurringServiceOut(BaseModel):
    id: int
    customer_id: int
    service_id: int
    recurrence_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    next_booking_date: datetime
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecurringServiceDetail(RecurringServiceOut):
    service: ServiceDetail


# ── Reminders ────────────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    recurring_service_id: int
    reminder_type: str = "email"  # email, sms, in_app
    scheduled_date: datetime
    message: Optional[str] = None


class ReminderMarkRead(BaseModel):
    is_read: bool


class ReminderOut(BaseModel):
    id: int
    recurring_service_id: int
    customer_id: int
    provider_id: int
    reminder_type: str
    reminder_status: str
    scheduled_date: datetime
    sent_at: Optional[datetime] = None
    message: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Skills & Expertise ───────────────────────────────────────────────────────

class SkillCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class SkillOut(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderSkillCreate(BaseModel):
    skill_id: int
    skill_level: str = "intermediate"


class ProviderSkillUpdate(BaseModel):
    skill_level: Optional[str] = None
    years_of_experience: Optional[int] = None


class ProviderSkillOut(BaseModel):
    id: int
    provider_id: int
    skill_id: int
    skill_level: str
    completed_jobs: int
    avg_rating: float
    percentile_rank: int
    verified: bool
    years_of_experience: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderSkillDetail(ProviderSkillOut):
    skill: SkillOut


class SkillReviewCreate(BaseModel):
    skill_id: int
    rating: int  # 1-5
    comment: Optional[str] = None
    would_rebook: bool = True


class SkillReviewOut(BaseModel):
    id: int
    booking_id: int
    provider_id: int
    skill_id: int
    rating: int
    comment: Optional[str] = None
    would_rebook: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin / Analytics ────────────────────────────────────────────────────────

class AnalyticsOut(BaseModel):
    total_users: int
    total_providers: int
    total_services: int
    total_bookings: int
    total_revenue: float
    pending_approvals: int
    bookings_by_status: dict
