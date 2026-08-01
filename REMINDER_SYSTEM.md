# Recurring Services & Reminders System

## Overview

The reminder system enables customers to set up recurring services that automatically generate bookings and send reminders at specified intervals. This is ideal for services like cleaning, maintenance, or regular grooming that customers need on a weekly, bi-weekly, or monthly basis.

## Features

### 1. **Recurring Services**
- Create recurring service subscriptions with customizable intervals
- Supported recurrence types: Weekly, Bi-weekly, Monthly
- Auto-generate bookings based on the recurrence pattern
- Pause/resume recurring services anytime
- Soft delete with history preservation

### 2. **Smart Reminders**
- Automatic reminder generation before each service
- Multiple reminder types: Email, SMS, In-app
- Scheduled reminders:
  - 1 day before service
  - 1 hour before service
- Track reminder status (Pending, Sent, Failed, Cancelled)
- Mark in-app reminders as read

### 3. **Background Scheduler**
- APScheduler-based automation
- Runs every minute to send due reminders
- Processes recurring services every 30 minutes
- Handles failed reminders gracefully

## Architecture

### Database Models

#### RecurringService
```python
{
  "id": int,
  "customer_id": int,
  "service_id": int,
  "recurrence_type": "weekly|biweekly|monthly",
  "start_date": datetime,
  "end_date": datetime | null,
  "next_booking_date": datetime,
  "is_active": bool,
  "notes": str | null,
  "created_at": datetime,
  "updated_at": datetime
}
```

#### Reminder
```python
{
  "id": int,
  "recurring_service_id": int,
  "customer_id": int,
  "provider_id": int,
  "reminder_type": "email|sms|in_app",
  "reminder_status": "pending|sent|failed|cancelled",
  "scheduled_date": datetime,
  "sent_at": datetime | null,
  "message": str | null,
  "is_read": bool,
  "created_at": datetime
}
```

## API Endpoints

### Recurring Services

#### Create Recurring Service
```http
POST /api/recurring-services
Authorization: Bearer {token}
Content-Type: application/json

{
  "service_id": 1,
  "recurrence_type": "weekly",
  "start_date": "2026-04-13T10:00:00Z",
  "end_date": null,
  "notes": "Weekly cleaning service"
}
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "service_id": 1,
  "recurrence_type": "weekly",
  "start_date": "2026-04-13T10:00:00Z",
  "end_date": null,
  "next_booking_date": "2026-04-13T10:00:00Z",
  "is_active": true,
  "notes": "Weekly cleaning service",
  "created_at": "2026-04-13T...",
  "updated_at": "2026-04-13T..."
}
```

#### List Recurring Services
```http
GET /api/recurring-services?skip=0&limit=20
Authorization: Bearer {token}
```

#### Get Specific Recurring Service
```http
GET /api/recurring-services/{recurring_id}
Authorization: Bearer {token}
```

#### Update Recurring Service
```http
PATCH /api/recurring-services/{recurring_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "recurrence_type": "biweekly",
  "is_active": false,
  "end_date": "2026-12-31T00:00:00Z"
}
```

#### Delete (Cancel) Recurring Service
```http
DELETE /api/recurring-services/{recurring_id}
Authorization: Bearer {token}
```

### Reminders

#### List All Reminders
```http
GET /api/recurring-services/reminders/all?status=pending&reminder_type=email&skip=0&limit=50
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: Filter by status (pending, sent, failed, cancelled)
- `reminder_type`: Filter by type (email, sms, in_app)
- `skip`: Pagination offset
- `limit`: Results per page

#### List Reminders for Specific Service
```http
GET /api/recurring-services/{recurring_id}/reminders
Authorization: Bearer {token}
```

#### Get Specific Reminder
```http
GET /api/recurring-services/reminders/{reminder_id}
Authorization: Bearer {token}
```

#### Mark Reminder as Read
```http
PATCH /api/recurring-services/reminders/{reminder_id}/read
Authorization: Bearer {token}
Content-Type: application/json

{
  "is_read": true
}
```

#### Get Upcoming Reminders Statistics
```http
GET /api/recurring-services/stats/upcoming?days=7
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_upcoming": 5,
  "by_type": {
    "email": 3,
    "in_app": 2,
    "sms": 0
  },
  "date_range": {
    "from": "2026-04-13T...",
    "to": "2026-04-20T..."
  }
}
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# SMTP Configuration for Email Reminders
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Database
DATABASE_URL=postgresql://user:password@localhost/urbanclap_db
```

### Dependencies

Add to `requirements.txt`:
```
APScheduler==3.10.4
emails==0.6
```

## Usage Flow

### 1. Customer Creates Recurring Service

```python
# POST /api/recurring-services
{
  "service_id": 5,  # e.g., Weekly Home Cleaning
  "recurrence_type": "weekly",
  "start_date": "2026-04-20",
  "end_date": "2026-12-31"  # Optional
}
```

### 2. System Creates Bookings Automatically

When the scheduler processes recurring services:
- Creates a new booking for the customer
- Generates two reminders:
  - Email reminder 1 day before
  - In-app reminder 1 hour before

### 3. Reminders are Sent

The scheduler checks every minute for pending reminders:
- **Email reminders** are sent via SMTP
- **In-app reminders** are marked as ready for display
- Status is updated to "sent" or "failed"

### 4. Customer Manages Reminders

Customers can:
- View upcoming reminders
- Mark in-app reminders as read
- View reminder history
- Cancel recurring services anytime

## Frontend Integration

### Display Recurring Services

```jsx
import RecurringServices from './components/RecurringServices';

// In your customer dashboard
<RecurringServices />
```

### Features in RecurringServices Component

- **View Active Services**: Shows all active recurring services
- **View Upcoming Reminders**: Displays pending and sent reminders
- **Manage Services**: Pause/resume or cancel services
- **Create New**: Set up new recurring services
- **Mark as Read**: For in-app reminders

## Scheduler Details

### Jobs

The scheduler runs two main jobs:

#### 1. Send Pending Reminders (Every minute)
```python
@scheduler.scheduled_job('cron', second=0)
def send_pending_reminders():
    # Check for reminders scheduled before now
    # Send email/in-app reminders
    # Mark as sent
    # Handle failures
```

#### 2. Process Recurring Services (Every 30 minutes)
```python
@scheduler.scheduled_job('cron', minute='*/30')
def process_recurring_services():
    # Find active recurring services with past next_booking_date
    # Create new bookings
    # Generate reminders
    # Update next_booking_date
```

### Error Handling

- Failed reminders are marked with status "failed"
- Logs include detailed error information
- System continues processing other reminders
- Admin can retry failed reminders manually

## Best Practices

### 1. Email Configuration
- Use environment variables for SMTP credentials
- Never commit `.env` file to version control
- Test email sending in development with a dummy SMTP server

### 2. Recurrence Patterns
- Weekly: Adds 7 days
- Bi-weekly: Adds 14 days
- Monthly: Adds 1 calendar month

### 3. Time Zones
- Store all times in UTC (datetime.utcnow())
- Convert to user's local timezone on frontend

### 4. Reminder Customization
- 1 day before: Good for preparation
- 1 hour before: Last-minute confirmation
- Can be extended in `scheduler.py`'s `create_reminders_for_service()`

## Extending the System

### Add SMS Reminders

1. **Backend**: Update `send_pending_reminders()` in `scheduler.py`:
```python
elif reminder.reminder_type == "sms":
    send_sms_reminder(db, reminder)
```

2. **Email Utility**: Add SMS function using Twilio or similar

### Add Custom Recurrence

Update `calculate_next_date()` in `scheduler.py` to support custom intervals like "every 3 days".

### Add Push Notifications

Integrate Firebase Cloud Messaging (FCM) for push notifications on mobile.

## Troubleshooting

### Reminders Not Sending

1. **Check scheduler is running**: Verify in application logs
2. **Check database**: Confirm reminders exist and are pending
3. **Check SMTP config**: Verify email credentials in `.env`
4. **Check logs**: Look for error messages in `scheduler.py`

### Bookings Not Creating

1. **Check for active recurring services**: Query database
2. **Verify next_booking_date**: Should be ≤ current time
3. **Check scheduler job**: Ensure it's running every 30 minutes
4. **Review error logs**: Check for duplicate booking prevention

### Performance Optimization

- Add indexes on frequently queried columns:
  ```sql
  CREATE INDEX idx_reminder_status ON reminders(reminder_status);
  CREATE INDEX idx_recurring_active ON recurring_services(is_active);
  ```

- Batch process reminders in larger intervals if needed
- Archive old completed reminders to separate table

## Testing

### Unit Test Example
```python
def test_create_recurring_service(client, auth_headers):
    response = client.post(
        "/api/recurring-services",
        headers=auth_headers,
        json={
            "service_id": 1,
            "recurrence_type": "weekly",
            "start_date": "2026-04-13T10:00:00Z"
        }
    )
    assert response.status_code == 201
    assert response.json()["recurrence_type"] == "weekly"
```

### Integration Test Example
```python
def test_reminder_generation(db):
    # Create recurring service
    recurring = RecurringService(...)
    db.add(recurring)
    db.commit()
    
    # Run scheduler
    from app.utils.scheduler import process_recurring_services
    process_recurring_services()
    
    # Check reminders created
    reminders = db.query(Reminder).filter(
        Reminder.recurring_service_id == recurring.id
    ).all()
    assert len(reminders) == 2  # 1 day and 1 hour before
```

## Support & Maintenance

- Monitor scheduler logs regularly
- Archive completed reminders monthly
- Update email templates for branding
- Test email sending periodically
- Review failed reminders and retry if needed
