# 🚀 Reminder System - Quick Integration Guide

## Installation Steps

### Step 1: Update Dependencies
```bash
cd backend
pip install APScheduler==3.10.4 emails==0.6
# Or update requirements.txt and run:
pip install -r requirements.txt
```

### Step 2: Database Migration
The models are already included. When you start the application, tables will be created automatically:

```sql
-- These tables will be created by SQLAlchemy on startup:
- recurring_services
- reminders
```

### Step 3: Configuration (Optional)
For email reminders, add to your `.env`:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# For Gmail: Generate an App Password
# https://support.google.com/accounts/answer/185833
```

### Step 4: Start Backend with Scheduler
```bash
cd backend
uvicorn app.main:app --reload
```

The scheduler will automatically start and run in the background.

### Step 5: Add to Frontend Routes (Optional)
In `frontend/src/App.jsx`, add the RecurringServices component to your customer dashboard:

```jsx
import RecurringServices from './components/RecurringServices';

// In your routes:
{
  path: "/dashboard/recurring-services",
  element: <RecurringServices />
}
```

Or import in CustomerDashboard:
```jsx
import RecurringServices from './components/RecurringServices';

export const CustomerDashboard = () => {
  return (
    <>
      {/* existing content */}
      <RecurringServices />
    </>
  );
};
```

## Files Created/Modified

### ✅ New Files
1. **Backend**
   - `app/routers/reminders.py` - API endpoints
   - `app/utils/scheduler.py` - Background scheduler

2. **Frontend**
   - `src/components/RecurringServices.jsx` - UI component
   - `src/styles/RecurringServices.css` - Styling

3. **Documentation**
   - `REMINDER_SYSTEM.md` - Full documentation
   - `test_reminder_system.py` - Test cases

### ✅ Modified Files
1. **Backend**
   - `app/models/models.py` - Added RecurringService, Reminder models + enums
   - `app/schemas/schemas.py` - Added reminder/recurring schemas
   - `app/utils/email.py` - Added send_reminder_email()
   - `app/main.py` - Added scheduler startup/shutdown
   - `requirements.txt` - Added APScheduler, emails

2. **Frontend**
   - None (component is standalone)

## Testing

### Option 1: Manual API Testing
```bash
# Get your JWT token first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","password":"password"}'

# Create recurring service
curl -X POST http://localhost:8000/api/recurring-services \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "recurrence_type": "weekly",
    "start_date": "2026-04-13T10:00:00Z"
  }'
```

### Option 2: Run Test Suite
```bash
cd backend
pytest test_reminder_system.py -v
```

### Option 3: Check Scheduler Status
```bash
# Watch application logs
tail -f logs/app.log | grep -i "reminder\|scheduler\|recurring"

# Or query database
psql -U urbancare -d urbancare -c "SELECT * FROM reminders LIMIT 5;"
```

## Monitoring

### Check if Reminders are Being Sent

1. **Application Logs**
   ```
   INFO: Reminder 1 sent successfully
   INFO: Reminder scheduler started
   ```

2. **Database Queries**
   ```sql
   -- Check pending reminders
   SELECT COUNT(*) FROM reminders WHERE reminder_status = 'pending';

   -- Check sent reminders
   SELECT * FROM reminders WHERE reminder_status = 'sent' 
   ORDER BY sent_at DESC LIMIT 5;

   -- Check for failures
   SELECT * FROM reminders WHERE reminder_status = 'failed';

   -- Check recurring services
   SELECT * FROM recurring_services WHERE is_active = true;
   ```

3. **Email Testing** (if SMTP configured)
   - Check sender's email sent folder
   - Check recipient's inbox/spam

## API Examples

### Create Recurring Service
```bash
curl -X POST http://localhost:8000/api/recurring-services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "recurrence_type": "weekly",
    "start_date": "2026-04-20T10:00:00Z",
    "end_date": "2026-12-31T00:00:00Z",
    "notes": "Weekly home cleaning"
  }'
```

### List Recurring Services
```bash
curl -X GET "http://localhost:8000/api/recurring-services" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Upcoming Reminders
```bash
curl -X GET "http://localhost:8000/api/recurring-services/reminders/all?status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

### View Reminder Statistics
```bash
curl -X GET "http://localhost:8000/api/recurring-services/stats/upcoming?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Issue: Scheduler not starting
**Check:**
```python
# In main.py lifespan, verify it's called on startup
# Check app logs for: "Reminder scheduler started"
```

**Fix:**
- Ensure APScheduler is installed: `pip install APScheduler`
- Check that lifespan context manager is properly defined

### Issue: Reminders not sending
**Check:**
1. SMTP config in `.env` (for email reminders)
2. Database has pending reminders: 
   ```sql
   SELECT * FROM reminders WHERE reminder_status = 'pending';
   ```
3. Check application logs for errors

**Fix:**
- Verify email credentials are correct
- Check that SMTP server allows connections from your IP
- For Gmail, use App Password instead of account password

### Issue: Bookings not creating automatically
**Check:**
```sql
SELECT * FROM recurring_services WHERE is_active = true;
SELECT * FROM bookings WHERE notes LIKE '%recurring%';
```

**Fix:**
- Ensure recurring service `start_date` is in the past
- Check that next_booking_date is <= current time
- Verify scheduler job is running: "Process recurring services"

## Deployment Notes

### Docker Setup
The services are already included in requirements.txt. No additional configuration needed.

### Environment Variables
Set these in your `.env` or deployment platform:
```env
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
DATABASE_URL=
SECRET_KEY=
```

### Scaling Considerations
For production with multiple instances:
1. Use a shared database (PostgreSQL)
2. Consider using a distributed job queue (Celery + Redis)
3. Replace APScheduler with APScheduler + distributed database backend

Simple guide to switch to distributed scheduler:
```python
# Instead of BackgroundScheduler:
from apscheduler.schedulers.background import BackgroundScheduler
# Use:
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
```

## Support

For issues or questions:
1. Check [REMINDER_SYSTEM.md](REMINDER_SYSTEM.md) for full documentation
2. Review [test_reminder_system.py](test_reminder_system.py) for examples
3. Check application logs for error messages
4. Query the database to verify data consistency

## Next Steps

1. ✅ Install and configure
2. ✅ Test with API endpoints
3. ✅ Integrate with frontend
4. ✅ Monitor for a few cycles
5. ✅ Roll out to production
6. Optional: Customize reminder templates/timing
7. Optional: Add SMS reminders via Twilio
8. Optional: Add push notifications via Firebase

---

**Happy recurring services! 🎉**
