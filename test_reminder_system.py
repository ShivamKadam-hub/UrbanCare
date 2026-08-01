"""
Test script for the Reminder System
Demonstrates usage of recurring services and reminders API
"""

import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Assuming you have test fixtures set up
def test_create_recurring_service(client, auth_headers_customer):
    """Test creating a recurring service"""
    response = client.post(
        "/api/recurring-services",
        headers=auth_headers_customer,
        json={
            "service_id": 1,
            "recurrence_type": "weekly",
            "start_date": datetime.utcnow().isoformat(),
            "notes": "Weekly home cleaning"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["recurrence_type"] == "weekly"
    assert data["is_active"] == True
    return data["id"]


def test_list_recurring_services(client, auth_headers_customer):
    """Test listing recurring services"""
    response = client.get(
        "/api/recurring-services",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)


def test_update_recurring_service(client, auth_headers_customer, recurring_service_id):
    """Test updating a recurring service"""
    response = client.patch(
        f"/api/recurring-services/{recurring_service_id}",
        headers=auth_headers_customer,
        json={
            "recurrence_type": "biweekly",
            "is_active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["recurrence_type"] == "biweekly"
    assert data["is_active"] == False


def test_delete_recurring_service(client, auth_headers_customer, recurring_service_id):
    """Test deleting (cancelling) a recurring service"""
    response = client.delete(
        f"/api/recurring-services/{recurring_service_id}",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 204


def test_list_reminders(client, auth_headers_customer):
    """Test listing reminders for current user"""
    response = client.get(
        "/api/recurring-services/reminders/all",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    reminders = response.json()
    assert isinstance(reminders, list)


def test_list_reminders_by_status(client, auth_headers_customer):
    """Test filtering reminders by status"""
    response = client.get(
        "/api/recurring-services/reminders/all?status=pending",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    reminders = response.json()
    for reminder in reminders:
        assert reminder["reminder_status"] == "pending"


def test_list_reminders_by_type(client, auth_headers_customer):
    """Test filtering reminders by type"""
    response = client.get(
        "/api/recurring-services/reminders/all?reminder_type=email",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    reminders = response.json()
    for reminder in reminders:
        assert reminder["reminder_type"] == "email"


def test_list_service_reminders(client, auth_headers_customer, recurring_service_id):
    """Test listing reminders for a specific recurring service"""
    response = client.get(
        f"/api/recurring-services/{recurring_service_id}/reminders",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    reminders = response.json()
    assert isinstance(reminders, list)


def test_mark_reminder_as_read(client, auth_headers_customer, reminder_id):
    """Test marking a reminder as read"""
    response = client.patch(
        f"/api/recurring-services/reminders/{reminder_id}/read",
        headers=auth_headers_customer,
        json={"is_read": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] == True


def test_get_upcoming_reminders_stats(client, auth_headers_customer):
    """Test getting upcoming reminders statistics"""
    response = client.get(
        "/api/recurring-services/stats/upcoming?days=7",
        headers=auth_headers_customer
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_upcoming" in data
    assert "by_type" in data
    assert "date_range" in data


def test_recurring_service_authorization(client, auth_headers_customer, auth_headers_other_customer, recurring_service_id):
    """Test that customers can only access their own recurring services"""
    # Other customer tries to access someone else's service
    response = client.get(
        f"/api/recurring-services/{recurring_service_id}",
        headers=auth_headers_other_customer
    )
    
    assert response.status_code == 403


def test_scheduler_sends_reminders(db: Session):
    """Test that the scheduler sends pending reminders"""
    from app.utils.scheduler import send_pending_reminders
    from app.models.models import Reminder, ReminderStatus
    
    # Manually run the send_pending_reminders function
    send_pending_reminders()
    
    # Check that pending reminders are now sent
    pending = db.query(Reminder).filter(
        Reminder.reminder_status == ReminderStatus.PENDING
    ).count()
    
    # Most should be processed
    assert pending < 10  # Adjust based on your test data


def test_calculate_next_date():
    """Test the calculate_next_date function"""
    from app.utils.scheduler import calculate_next_date
    
    test_date = datetime(2026, 4, 13, 10, 0, 0)
    
    # Weekly
    next_weekly = calculate_next_date(test_date, "weekly")
    assert next_weekly == datetime(2026, 4, 20, 10, 0, 0)
    
    # Bi-weekly
    next_biweekly = calculate_next_date(test_date, "biweekly")
    assert next_biweekly == datetime(2026, 4, 27, 10, 0, 0)
    
    # Monthly
    next_monthly = calculate_next_date(test_date, "monthly")
    assert next_monthly == datetime(2026, 5, 13, 10, 0, 0)


# ────────────────────────────────────────────────────────────────────────────
# MANUAL TESTING GUIDE
# ────────────────────────────────────────────────────────────────────────────

"""
### Manual API Testing with cURL

1. Login and get token:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","password":"password"}'
```

2. Create a service (as provider first):
```bash
curl -X POST http://localhost:8000/api/services \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "title": "Weekly Cleaning",
    "price": 500,
    "duration_minutes": 60
  }'
```

3. Create recurring service:
```bash
curl -X POST http://localhost:8000/api/recurring-services \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "recurrence_type": "weekly",
    "start_date": "2026-04-13T10:00:00Z",
    "notes": "My weekly cleaning"
  }'
```

4. List reminders:
```bash
curl -X GET http://localhost:8000/api/recurring-services/reminders/all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

5. Get upcoming stats:
```bash
curl -X GET "http://localhost:8000/api/recurring-services/stats/upcoming?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Testing in Python

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Create recurring service
response = requests.post(
    f"{BASE_URL}/api/recurring-services",
    headers=HEADERS,
    json={
        "service_id": 1,
        "recurrence_type": "weekly",
        "start_date": datetime.utcnow().isoformat()
    }
)
print(response.json())

# List reminders
response = requests.get(
    f"{BASE_URL}/api/recurring-services/reminders/all",
    headers=HEADERS
)
print(json.dumps(response.json(), indent=2))

# Get stats
response = requests.get(
    f"{BASE_URL}/api/recurring-services/stats/upcoming?days=7",
    headers=HEADERS
)
print(json.dumps(response.json(), indent=2))
```

### Monitoring the Scheduler

Check if reminders are being sent:
1. Check application logs for scheduler messages
2. Query the database for reminder status updates:
   ```sql
   SELECT id, reminder_status, sent_at FROM reminders 
   ORDER BY created_at DESC LIMIT 10;
   ```
3. Check email delivery (if SMTP is configured)
4. Monitor database for new auto-generated bookings
"""
