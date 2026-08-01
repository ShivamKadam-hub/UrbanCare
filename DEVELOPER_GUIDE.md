# 👨‍💻 Developer's Guide - Extending the Reminder System

This guide shows you how to extend and customize the reminder system for your specific needs.

## 🔧 Common Customizations

### 1. Add SMS Reminders

#### Step 1: Add Twilio to requirements.txt
```
twilio==8.2.0
```

#### Step 2: Create SMS function in email.py
```python
from twilio.rest import Client

TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_FROM_NUMBER = settings.TWILIO_FROM_NUMBER

def send_sms_reminder(to_phone: str, message: str) -> bool:
    """Send SMS reminder using Twilio"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=to_phone
        )
        return True
    except Exception as exc:
        print(f"[SMS ERROR] {exc}")
        return False
```

#### Step 3: Update scheduler.py
```python
def send_pending_reminders():
    # ... existing code ...
    elif reminder.reminder_type == "sms":
        send_sms_reminder(
            to_phone=reminder.customer.phone,
            message=reminder.message
        )
```

#### Step 4: Add .env variables
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
```

### 2. Add Push Notifications

#### Step 1: Add Firebase to requirements.txt
```
firebase-admin==6.1.0
```

#### Step 2: Set up Firebase credentials
```python
# config.py
import firebase_admin
from firebase_admin import credentials

def init_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# In main.py startup
init_firebase()
```

#### Step 3: Create push notification function
```python
# utils/notifications.py
from firebase_admin import messaging

def send_push_notification(user_id: int, title: str, body: str, db: Session):
    """Send push notification via Firebase"""
    # Get user's FCM token from database (need to add this field)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.fcm_token:
        return False
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=user.fcm_token,
        )
        response = messaging.send(message)
        return True
    except Exception as exc:
        print(f"[PUSH ERROR] {exc}")
        return False
```

### 3. Customize Reminder Timing

#### Current: 1 day + 1 hour before
#### Add: Custom intervals

```python
# In scheduler.py - create_reminders_for_service()
def create_reminders_for_service(
    db: Session, 
    recurring: RecurringService, 
    booking_id: int
):
    service = recurring.service
    scheduled_datetime = datetime.strptime(
        recurring.next_booking_date.strftime("%Y-%m-%d") + " 10:00",
        "%Y-%m-%d %H:%M"
    )
    
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == service.provider_id
    ).first()
    
    # Define reminders with custom timing
    reminder_configs = [
        {"hours": 72, "message": "Your service is in 3 days", "type": "email"},
        {"hours": 24, "message": "Your service is tomorrow", "type": "email"},
        {"hours": 1, "message": "Your service starts in 1 hour", "type": "in_app"},
    ]
    
    for config in reminder_configs:
        reminder = Reminder(
            recurring_service_id=recurring.id,
            customer_id=recurring.customer_id,
            provider_id=provider.id,
            reminder_type=config["type"],
            scheduled_date=scheduled_datetime - timedelta(hours=config["hours"]),
            message=config["message"]
        )
        db.add(reminder)
    
    db.flush()
```

### 4. Add Custom Recurrence Patterns

#### Extend calculate_next_date()
```python
def calculate_next_date(current_date: datetime, recurrence_type: str) -> datetime:
    """Enhanced recurrence calculation"""
    if recurrence_type == RecurrenceType.WEEKLY:
        return current_date + timedelta(days=7)
    elif recurrence_type == RecurrenceType.BIWEEKLY:
        return current_date + timedelta(days=14)
    elif recurrence_type == RecurrenceType.MONTHLY:
        if current_date.month == 12:
            return current_date.replace(year=current_date.year + 1, month=1)
        else:
            return current_date.replace(month=current_date.month + 1)
    elif recurrence_type == "daily":
        return current_date + timedelta(days=1)
    elif recurrence_type == "quarterly":
        month = (current_date.month + 3) % 12
        year = current_date.year + (1 if month < current_date.month else 0)
        return current_date.replace(year=year, month=month)
    elif recurrence_type == "custom":
        # Could fetch custom interval from database
        return current_date + timedelta(days=7)
    else:
        return current_date + timedelta(days=7)
```

#### Update enum in models.py
```python
class RecurrenceType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"
```

### 5. Add Reminder Scheduling Configuration

#### Create a new model
```python
# In models.py
class ReminderConfiguration(Base):
    __tablename__ = "reminder_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reminder_days_before = Column(Integer, default=1)
    reminder_hours_before = Column(Integer, default=1)
    enable_email = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)
    enable_push = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    customer = relationship("User")
```

#### Use in scheduler
```python
def create_reminders_for_service(db: Session, recurring: RecurringService):
    # Get customer's preferences
    config = db.query(ReminderConfiguration).filter(
        ReminderConfiguration.customer_id == recurring.customer_id
    ).first()
    
    if not config:
        config = ReminderConfiguration(customer_id=recurring.customer_id)
    
    # Create reminders based on preferences
    if config.enable_email:
        reminder = Reminder(
            ...,
            reminder_type="email",
            scheduled_date=...,
            ...
        )
```

### 6. Add Analytics/Reporting

#### Create admin endpoint
```python
# In reminders.py
@router.get("/admin/stats/overview", response_model=dict)
def get_reminder_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin endpoint for reminder statistics"""
    total_reminders = db.query(Reminder).count()
    sent_count = db.query(Reminder).filter(
        Reminder.reminder_status == ReminderStatus.SENT
    ).count()
    failed_count = db.query(Reminder).filter(
        Reminder.reminder_status == ReminderStatus.FAILED
    ).count()
    
    active_recurring = db.query(RecurringService).filter(
        RecurringService.is_active == True
    ).count()
    
    return {
        "total_reminders": total_reminders,
        "sent": sent_count,
        "failed": failed_count,
        "pending": total_reminders - sent_count - failed_count,
        "active_services": active_recurring,
        "success_rate": (sent_count / total_reminders * 100) if total_reminders > 0 else 0
    }
```

## 🔄 Advanced Patterns

### 1. Retry Failed Reminders

```python
@router.post("/admin/reminders/retry-failed")
def retry_failed_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Retry sending failed reminders"""
    failed_reminders = db.query(Reminder).filter(
        Reminder.reminder_status == ReminderStatus.FAILED
    ).all()
    
    retry_count = 0
    for reminder in failed_reminders:
        try:
            if reminder.reminder_type == "email":
                send_email_reminder(db, reminder)
            
            reminder.reminder_status = ReminderStatus.SENT
            reminder.sent_at = datetime.utcnow()
            db.commit()
            retry_count += 1
        except Exception as e:
            print(f"Retry failed for reminder {reminder.id}: {e}")
    
    return {"retried": retry_count, "total_failed": len(failed_reminders)}
```

### 2. Bulk Operations

```python
@router.patch("/admin/recurring-services/bulk-update")
def bulk_update_recurring_services(
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Bulk update multiple recurring services"""
    recurring_ids = updates.get("ids", [])
    new_status = updates.get("is_active")
    
    updated = db.query(RecurringService).filter(
        RecurringService.id.in_(recurring_ids)
    ).update({"is_active": new_status})
    
    db.commit()
    return {"updated_count": updated}
```

### 3. Intelligent Scheduling

```python
def should_send_reminder(reminder: Reminder) -> bool:
    """Implement smart logic for sending reminders"""
    # Don't send if customer already marked as read
    if reminder.is_read:
        return False
    
    # Don't send duplicate reminders
    similar_sent = db.query(Reminder).filter(
        Reminder.recurring_service_id == reminder.recurring_service_id,
        Reminder.reminder_type == reminder.reminder_type,
        Reminder.reminder_status == ReminderStatus.SENT,
        Reminder.scheduled_date.between(
            reminder.scheduled_date - timedelta(hours=1),
            reminder.scheduled_date + timedelta(hours=1)
        )
    ).count()
    
    if similar_sent > 0:
        return False
    
    return True
```

## 🧩 Integration Examples

### 1. Integrate with Notification Center

```jsx
// Frontend - Add to Navbar or Dashboard
const NotificationBell = () => {
  const [unreadReminders, setUnreadReminders] = useState([]);
  
  useEffect(() => {
    fetchUnreadReminders();
    // Poll every minute
    const interval = setInterval(fetchUnreadReminders, 60000);
    return () => clearInterval(interval);
  }, []);
  
  const fetchUnreadReminders = async () => {
    const response = await axios.get(
      '/api/recurring-services/reminders/all?is_read=false',
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setUnreadReminders(response.data);
  };
  
  return (
    <div className="notification-bell">
      🔔 <span className="badge">{unreadReminders.length}</span>
    </div>
  );
};
```

### 2. Calendar Integration

```jsx
// Show recurring services and reminders on calendar
import Calendar from 'react-calendar';

const RecurringServiceCalendar = ({ reminders }) => {
  const tileContent = ({ date }) => {
    const dayReminders = reminders.filter(r => 
      new Date(r.scheduled_date).toDateString() === date.toDateString()
    );
    
    return dayReminders.length > 0 ? (
      <div className="reminder-indicator">{dayReminders.length}</div>
    ) : null;
  };
  
  return <Calendar tileContent={tileContent} />;
};
```

## 🔒 Security Considerations

### 1. Rate Limiting
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.util import get_remote_address

# Apply to recurring-services endpoints
@app.get("/api/recurring-services")
@FastAPILimiter(key_func=get_remote_address, limit="100/minute")
```

### 2. Audit Logging
```python
# Log all reminder operations
def log_reminder_action(user_id: int, action: str, reminder_id: int):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="reminder",
        entity_id=reminder_id,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
```

### 3. Data Privacy
```python
# Encrypt sensitive fields in reminders
from cryptography.fernet import Fernet

# Store encrypted phone/address in reminders
reminder.encrypted_data = encrypt(user_phone, ENCRYPTION_KEY)
```

## 📝 Testing Enhancements

### Add Performance Tests
```python
import time

def test_scheduler_performance():
    """Test scheduler processes 1000 reminders in <5s"""
    # Create 1000 pending reminders
    reminders = [create_test_reminder() for _ in range(1000)]
    db.add_all(reminders)
    db.commit()
    
    start = time.time()
    send_pending_reminders()
    elapsed = time.time() - start
    
    assert elapsed < 5, f"Scheduler took {elapsed}s, expected < 5s"
```

### Add Load Tests
```python
import concurrent.futures

def test_concurrent_recurring_creation():
    """Test creating 100 recurring services concurrently"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(create_recurring_service, service_id=i)
            for i in range(100)
        ]
        results = [f.result() for f in futures]
    
    assert len(results) == 100
```

## 🚀 Performance Optimization

### 1. Database Indexing
```python
# In models.py
class Reminder(Base):
    __tablename__ = "reminders"
    
    # ... columns ...
    
    __table_args__ = (
        Index('idx_reminder_status_scheduled', 'reminder_status', 'scheduled_date'),
        Index('idx_reminder_customer', 'customer_id'),
    )
```

### 2. Batch Processing
```python
def send_pending_reminders_batched(batch_size: int = 100):
    """Process reminders in batches for better performance"""
    offset = 0
    while True:
        batch = db.query(Reminder).filter(
            Reminder.reminder_status == ReminderStatus.PENDING
        ).offset(offset).limit(batch_size).all()
        
        if not batch:
            break
        
        for reminder in batch:
            send_reminder(reminder)
        
        offset += batch_size
```

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_reminder_preferences(user_id: int):
    """Cache user preferences"""
    return db.query(ReminderConfiguration).filter(
        ReminderConfiguration.customer_id == user_id
    ).first()
```

## 📚 References

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Twilio Python Documentation](https://www.twilio.com/docs/libraries/python)
- [Firebase Admin Python](https://firebase.google.com/docs/admin/setup)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/)

---

**Happy coding! 🚀**

For questions or issues, refer back to `REMINDER_SYSTEM.md` for the complete documentation.
