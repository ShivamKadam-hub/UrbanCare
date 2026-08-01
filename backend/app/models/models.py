import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint, Table,
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


recurring_service_bookings = Table(
    "recurring_service_bookings",
    Base.metadata,
    Column("recurring_service_id", Integer, ForeignKey("recurring_services.id"), primary_key=True),
    Column("booking_id", Integer, ForeignKey("bookings.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)


# ── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class RecurrenceType(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReminderType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    MASTER = "master"


# ── Users ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    provider_profile = relationship("ServiceProvider", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="customer", foreign_keys="Booking.customer_id")
    reviews = relationship("Review", back_populates="customer")


# ── Service Providers ────────────────────────────────────────────────────────

class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="provider_profile")
    services = relationship("Service", back_populates="provider", cascade="all, delete-orphan")
    skills = relationship("ProviderSkill", back_populates="provider", cascade="all, delete-orphan")


# ── Categories ───────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    services = relationship("Service", back_populates="category")


# ── Services ─────────────────────────────────────────────────────────────────

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=60)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    provider = relationship("ServiceProvider", back_populates="services")
    category = relationship("Category", back_populates="services")
    bookings = relationship("Booking", back_populates="service")
    reviews = relationship("Review", back_populates="service")


# ── Bookings ─────────────────────────────────────────────────────────────────

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    booking_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    time_slot = Column(String(20), nullable=False)       # e.g. "10:00-11:00"
    address = Column(Text, nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("User", back_populates="bookings", foreign_keys=[customer_id])
    service = relationship("Service", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    review = relationship("Review", back_populates="booking", uselist=False)


# ── Payments ─────────────────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(50), default="card")  # card, upi, wallet
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String(200), nullable=True)
    stripe_session_id = Column(String(255), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    paid_at = Column(DateTime, nullable=True)

    booking = relationship("Booking", back_populates="payment")


# ── Reviews ──────────────────────────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("booking_id", name="uq_review_booking"),
    )

    booking = relationship("Booking", back_populates="review")
    customer = relationship("User", back_populates="reviews")
    service = relationship("Service", back_populates="reviews")


# ── Recurring Services ───────────────────────────────────────────────────────

class RecurringService(Base):
    __tablename__ = "recurring_services"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    recurrence_type = Column(SAEnum(RecurrenceType), nullable=False)  # weekly, biweekly, monthly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for ongoing
    next_booking_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    customer = relationship("User")
    service = relationship("Service")
    bookings_generated = relationship("Booking", secondary="recurring_service_bookings", viewonly=True)
    reminders = relationship("Reminder", back_populates="recurring_service", cascade="all, delete-orphan")


# ── Reminders ────────────────────────────────────────────────────────────────

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    recurring_service_id = Column(Integer, ForeignKey("recurring_services.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    reminder_type = Column(SAEnum(ReminderType), default=ReminderType.EMAIL)  # email, sms, in_app
    reminder_status = Column(SAEnum(ReminderStatus), default=ReminderStatus.PENDING)
    scheduled_date = Column(DateTime, nullable=False)  # When reminder should be sent
    sent_at = Column(DateTime, nullable=True)  # When reminder was actually sent
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)  # For in-app reminders
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    recurring_service = relationship("RecurringService", back_populates="reminders")
    customer = relationship("User")
    provider = relationship("ServiceProvider")


# ── Skills & Expertise ───────────────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    category = relationship("Category")
    provider_skills = relationship("ProviderSkill", back_populates="skill", cascade="all, delete-orphan")


class ProviderSkill(Base):
    __tablename__ = "provider_skills"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_level = Column(SAEnum(SkillLevel), default=SkillLevel.INTERMEDIATE)
    completed_jobs = Column(Integer, default=0)  # Number of jobs completed with this skill
    avg_rating = Column(Float, default=0.0)  # Average rating for this specific skill
    percentile_rank = Column(Integer, default=50)  # Top X% (0-100)
    verified = Column(Boolean, default=False)  # Admin verified expertise
    years_of_experience = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("provider_id", "skill_id", name="uq_provider_skill"),
    )

    provider = relationship("ServiceProvider", back_populates="skills")
    skill = relationship("Skill", back_populates="provider_skills")


class SkillReview(Base):
    __tablename__ = "skill_reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating for this specific skill
    comment = Column(Text, nullable=True)
    would_rebook = Column(Boolean, default=True)  # Would customer rebook this provider for this skill?
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    booking = relationship("Booking")
    provider = relationship("ServiceProvider")
    skill = relationship("Skill")
