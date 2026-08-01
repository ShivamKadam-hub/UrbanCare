"""
Reminder Scheduler - APScheduler integration for sending reminders
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.database import SessionLocal
from app.models.models import (
    Reminder, RecurringService, RecurrenceType, ReminderStatus,
    Booking, BookingStatus
)
from app.utils.email import send_reminder_email

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:  # pragma: no cover - environment dependent
    BackgroundScheduler = None
    CronTrigger = None

# Global scheduler instance (optional in dev environments)
scheduler = BackgroundScheduler() if BackgroundScheduler else None


def send_pending_reminders():
    """
    Check for pending reminders and send them
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Get all pending reminders that are scheduled for now or earlier
        pending_reminders = db.query(Reminder).filter(
            Reminder.reminder_status == ReminderStatus.PENDING,
            Reminder.scheduled_date <= now
        ).all()
        
        for reminder in pending_reminders:
            try:
                if reminder.reminder_type == "email":
                    send_email_reminder(db, reminder)
                elif reminder.reminder_type == "in_app":
                    mark_in_app_reminder_sent(db, reminder)
                # SMS functionality can be added later
                
                # Mark as sent
                reminder.reminder_status = ReminderStatus.SENT
                reminder.sent_at = datetime.utcnow()
                db.commit()
                logger.info(f"Reminder {reminder.id} sent successfully")
            except Exception as e:
                logger.error(f"Failed to send reminder {reminder.id}: {str(e)}")
                reminder.reminder_status = ReminderStatus.FAILED
                db.commit()
    except Exception as e:
        logger.error(f"Error in send_pending_reminders: {str(e)}")
    finally:
        db.close()


def send_email_reminder(db: Session, reminder: Reminder):
    """Send email reminder"""
    recurring_service = db.query(RecurringService).filter(
        RecurringService.id == reminder.recurring_service_id
    ).first()
    
    if not recurring_service or not recurring_service.service:
        logger.error(f"RecurringService not found for reminder {reminder.id}")
        return
    
    try:
        send_reminder_email(
            email=reminder.customer.email if reminder.customer else "",
            customer_name=reminder.customer.name if reminder.customer else "Customer",
            service_name=recurring_service.service.title,
            reminder_message=reminder.message or f"Reminder for your upcoming {recurring_service.service.title} service",
            scheduled_date=reminder.scheduled_date
        )
    except Exception as e:
        logger.error(f"Failed to send email reminder: {str(e)}")
        raise


def mark_in_app_reminder_sent(db: Session, reminder: Reminder):
    """Mark in-app reminder as processed"""
    logger.info(f"In-app reminder {reminder.id} marked for display")


def process_recurring_services():
    """
    Process recurring services and create new bookings + reminders
    Called periodically to generate upcoming bookings and their reminders
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Get all active recurring services
        active_recurring = db.query(RecurringService).filter(
            RecurringService.is_active == True,
            RecurringService.start_date <= now,
            (RecurringService.end_date.is_(None) | (RecurringService.end_date >= now))
        ).all()
        
        for recurring in active_recurring:
            try:
                # Check if next booking needs to be created
                if recurring.next_booking_date <= now:
                    process_recurring_booking(db, recurring)
            except Exception as e:
                logger.error(f"Error processing recurring service {recurring.id}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in process_recurring_services: {str(e)}")
    finally:
        db.close()


def process_recurring_booking(db: Session, recurring: RecurringService):
    """
    Create a new booking for a recurring service and schedule reminders
    """
    try:
        # Create booking for upcoming service
        # Calculate next execution time
        next_date = calculate_next_date(recurring.next_booking_date, recurring.recurrence_type)
        
        # Create booking
        booking = Booking(
            customer_id=recurring.customer_id,
            service_id=recurring.service_id,
            booking_date=recurring.next_booking_date.strftime("%Y-%m-%d"),
            time_slot="10:00-11:00",  # Default time, can be customized
            address="",  # Should be stored in RecurringService or fetched from customer
            status=BookingStatus.PENDING,
            notes=f"Auto-generated from recurring service #{recurring.id}"
        )
        db.add(booking)
        db.flush()
        
        # Create reminders for this booking
        create_reminders_for_service(db, recurring, booking.id)
        
        # Update next booking date
        recurring.next_booking_date = next_date
        db.commit()
        logger.info(f"Booking created for recurring service {recurring.id}")
    except Exception as e:
        logger.error(f"Error processing recurring booking: {str(e)}")
        raise


def create_reminders_for_service(db: Session, recurring: RecurringService, booking_id: int):
    """
    Create reminders for a service:
    - 1 day before
    - 1 hour before
    """
    from app.models.models import ServiceProvider
    
    service = recurring.service
    scheduled_datetime = datetime.strptime(
        recurring.next_booking_date.strftime("%Y-%m-%d") + " 10:00",
        "%Y-%m-%d %H:%M"
    )
    
    # Get provider
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == service.provider_id
    ).first()
    
    if not provider:
        logger.error(f"Provider not found for service {service.id}")
        return
    
    # Reminder 1 day before
    reminder_1day = Reminder(
        recurring_service_id=recurring.id,
        customer_id=recurring.customer_id,
        provider_id=provider.id,
        reminder_type="email",
        scheduled_date=scheduled_datetime - timedelta(days=1),
        message=f"Reminder: Your {service.title} service is scheduled for tomorrow at 10:00 AM"
    )
    db.add(reminder_1day)
    
    # Reminder 1 hour before
    reminder_1hour = Reminder(
        recurring_service_id=recurring.id,
        customer_id=recurring.customer_id,
        provider_id=provider.id,
        reminder_type="in_app",
        scheduled_date=scheduled_datetime - timedelta(hours=1),
        message=f"Reminder: Your {service.title} service starts in 1 hour"
    )
    db.add(reminder_1hour)
    
    db.flush()


def calculate_next_date(current_date: datetime, recurrence_type: str) -> datetime:
    """
    Calculate the next occurrence date based on recurrence type
    """
    if recurrence_type == RecurrenceType.WEEKLY:
        return current_date + timedelta(days=7)
    elif recurrence_type == RecurrenceType.BIWEEKLY:
        return current_date + timedelta(days=14)
    elif recurrence_type == RecurrenceType.MONTHLY:
        # Add one month
        if current_date.month == 12:
            return current_date.replace(year=current_date.year + 1, month=1)
        else:
            return current_date.replace(month=current_date.month + 1)
    else:
        return current_date + timedelta(days=7)


def start_scheduler():
    """Start the background scheduler"""
    if scheduler is None:
        logger.warning("APScheduler is not installed; reminder scheduler is disabled.")
        return

    if not scheduler.running:
        # Check and send reminders every minute
        scheduler.add_job(
            send_pending_reminders,
            CronTrigger(second=0),
            id="send_reminders",
            name="Send pending reminders",
            replace_existing=True
        )
        
        # Process recurring services every 30 minutes
        scheduler.add_job(
            process_recurring_services,
            CronTrigger(minute="*/30"),
            id="process_recurring",
            name="Process recurring services",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Reminder scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Reminder scheduler stopped")
