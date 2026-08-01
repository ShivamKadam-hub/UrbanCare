# UrbanCare — Home Services Marketplace

A full-stack web application similar to Urban Company, built with **FastAPI**, **React**, **PostgreSQL**, **JWT authentication**, and **Docker**.

---

## ✨ Features

### Customer
- Register/Login with JWT • Browse & search services • Filter by category
- Book appointments with date/time slots • Online payment (simulated)
- View booking history • Rate & review service providers
- ⭐ **NEW: Set up recurring services** • Automatic booking generation
- ⭐ **NEW: Smart reminders** • Email & in-app notifications
- ⭐ **NEW: Skill-based matching** • Find experts by specific skills, not just ratings

### Service Provider
- Register as provider • Add/manage services offered
- Accept/reject booking requests • Mark bookings complete
- View earnings dashboard
- ⭐ **NEW: Receive reminders** for upcoming bookings from recurring services
- ⭐ **NEW: Add expertise skills** • Build reputation in specific areas

### Admin
- Manage users & providers • Approve provider registrations
- CRUD categories & services • Analytics dashboard with charts
- View all bookings
- ⭐ **NEW: Monitor recurring services** • View all reminders and statistics
- ⭐ **NEW: Verify provider expertise** • Validate skill certifications

---

## 🏗 Tech Stack

| Layer      | Technology                            |
|------------|---------------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy      |
| Frontend   | React 18, Vite, React Router, Recharts |
| Database   | PostgreSQL 15                         |
| Auth       | JWT (python-jose + passlib/bcrypt)    |
| Deployment | Docker, Docker Compose                |
| Styling    | Custom CSS (glassmorphism, dark theme)|

---

## 📁 Project Structure

```
Urbanclap/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry
│   │   ├── config.py          # Environment config
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── seed.py            # Sample data seeder
│   │   ├── models/models.py   # ORM models (9 tables)
│   │   ├── schemas/schemas.py # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py        # /api/auth/*
│   │   │   ├── services.py    # /api/services/*
│   │   │   ├── bookings.py    # /api/bookings/*
│   │   │   ├── payments.py    # /api/payments/*
│   │   │   ├── reviews.py     # /api/reviews/*
│   │   │   ├── admin.py       # /api/admin/*
│   │   │   └── reminders.py   # /api/recurring-services/* ⭐ NEW
│   │   └── utils/
│   │       ├── auth.py        # JWT + password hashing
│   │       ├── email.py       # Email notifications
│   │       └── scheduler.py   # Background job scheduler ⭐ NEW
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/client.js      # Axios + JWT interceptor
│   │   ├── context/AuthContext.jsx
│   │   ├── components/        # Navbar, Footer, ServiceCard
│   │   │   └── RecurringServices.jsx   # ⭐ NEW
│   │   ├── pages/             # 9 page components
│   │   ├── styles/            # Component styles
│   │   │   └── RecurringServices.css   # ⭐ NEW
│   │   ├── App.jsx            # Router
│   │   ├── App.css            # Component styles
│   │   ├── index.css          # Design system
│   │   └── main.jsx           # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── README.md
├── REMINDER_SYSTEM.md          # ⭐ Full documentation
└── test_reminder_system.py     # ⭐ Test suite
```


---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start all services
docker-compose up --build

# Seed sample data
docker-compose exec backend python -m app.seed
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### Option 2: Run Locally

#### Prerequisites
- Python 3.11+, Node.js 18+, PostgreSQL 15+

#### Database Setup
```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE USER urbancare WITH PASSWORD 'urbancare123';"
psql -U postgres -c "CREATE DATABASE urbancare OWNER urbancare;"
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
# Edit .env if needed
uvicorn app.main:app --reload --port 8000

# Seed sample data (in another terminal)
cd backend
python -m app.seed
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 🔐 Sample Login Credentials

| Role     | Email                   | Password      |
|----------|-------------------------|---------------|
| Admin    | admin@urbancare.com     | admin123      |
| Provider | provider@urbancare.com  | provider123   |
| Customer | customer@urbancare.com  | customer123   |

> Run the seed script first: `python -m app.seed`

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint           | Description          |
|--------|--------------------|----------------------|
| POST   | /api/auth/register | Register user        |
| POST   | /api/auth/login    | Login & get JWT      |
| GET    | /api/auth/me       | Current user profile |

### Services
| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | /api/services         | List/search/filter     |
| GET    | /api/services/{id}    | Service detail         |
| POST   | /api/services         | Create (provider only) |
| PUT    | /api/services/{id}    | Update (provider only) |
| DELETE | /api/services/{id}    | Delete (provider only) |

### Bookings
| Method | Endpoint                       | Description      |
|--------|--------------------------------|------------------|
| POST   | /api/bookings                  | Create booking   |
| GET    | /api/bookings                  | List bookings    |
| GET    | /api/bookings/{id}             | Booking detail   |
| PATCH  | /api/bookings/{id}/status      | Update status    |

### Payments
| Method | Endpoint       | Description      |
|--------|----------------|------------------|
| POST   | /api/payments  | Process payment  |
| GET    | /api/payments  | Payment history  |

### Reviews
| Method | Endpoint                    | Description          |
|--------|-----------------------------|----------------------|
| POST   | /api/reviews                | Submit review        |
| GET    | /api/reviews/service/{id}   | Service reviews      |

### Admin
| Method | Endpoint                          | Description        |
|--------|-----------------------------------|--------------------|
| GET    | /api/admin/users                  | List users         |
| PATCH  | /api/admin/users/{id}/toggle      | Toggle user status |
| GET    | /api/admin/providers              | List providers     |
| PATCH  | /api/admin/providers/{id}/approve | Approve provider   |
| GET    | /api/admin/categories             | List categories    |
| POST   | /api/admin/categories             | Create category    |
| PUT    | /api/admin/categories/{id}        | Update category    |
| DELETE | /api/admin/categories/{id}        | Delete category    |
| GET    | /api/admin/bookings               | All bookings       |
| GET    | /api/admin/analytics              | Dashboard analytics|

### Recurring Services & Reminders ⭐ NEW
| Method | Endpoint                                    | Description              |
|--------|---------------------------------------------|--------------------------|
| POST   | /api/recurring-services                     | Create recurring service |
| GET    | /api/recurring-services                     | List recurring services  |
| GET    | /api/recurring-services/{id}                | Get service details      |
| PATCH  | /api/recurring-services/{id}                | Update recurring service |
| DELETE | /api/recurring-services/{id}                | Cancel recurring service |
| GET    | /api/recurring-services/reminders/all       | List all reminders       |
| GET    | /api/recurring-services/{id}/reminders      | Service reminders        |
| GET    | /api/recurring-services/reminders/{id}      | Get reminder details     |
| PATCH  | /api/recurring-services/reminders/{id}/read | Mark reminder as read    |
| GET    | /api/recurring-services/stats/upcoming      | Reminder statistics      |

### Skills & Expertise ⭐ NEW
| Method | Endpoint                                  | Description                 |
|--------|-------------------------------------------|-----------------------------|
| POST   | /api/skills                               | Create skill (admin)        |
| GET    | /api/skills                               | List all skills             |
| GET    | /api/skills/{id}                          | Get skill details           |
| POST   | /api/skills/provider/add                  | Add skill to profile        |
| GET    | /api/skills/provider/my-skills            | Get my skills               |
| GET    | /api/skills/provider/{id}                 | Get provider's skills       |
| DELETE | /api/skills/provider/remove/{id}          | Remove skill from profile   |
| POST   | /api/skills/reviews                       | Submit skill review         |
| GET    | /api/skills/reviews/provider/{id}         | Get provider skill reviews  |
| POST   | /api/skills/match                         | Find providers by skills    |
| GET    | /api/skills/expertise/{id}                | Get expertise summary       |
| GET    | /api/skills/trends/{id}                   | Get skill trends            |
| GET    | /api/skills/analytics/top-skills          | Top skills analytics        |

---

## 🔔 Reminder System

**New Feature:** Automatic recurring services with smart reminders!

### Overview
Customers can set up recurring services that automatically generate bookings and send reminders at specified intervals. Perfect for services like:
- Weekly home cleaning
- Monthly maintenance
- Regular grooming & salon services
- Periodic repairs

### Key Features
✅ **Recurring Bookings** - Weekly, Bi-weekly, or Monthly intervals  
✅ **Smart Reminders** - Email 1 day before, In-app 1 hour before  
✅ **Background Scheduler** - APScheduler-based automation  
✅ **Full Management** - Pause, resume, or cancel anytime  
✅ **Tracking** - View reminder history and status  

### Quick Start

```python
# 1. Frontend: Navigate to "Recurring Services" in customer dashboard
# 2. Create a recurring service:

POST /api/recurring-services
{
  "service_id": 1,
  "recurrence_type": "weekly",  // or "biweekly", "monthly"
  "start_date": "2026-04-20T10:00:00Z"
}

# 3. System automatically:
#    - Creates bookings on schedule
#    - Generates reminders
#    - Sends notifications

# 4. View upcoming reminders:
GET /api/recurring-services/reminders/all
```

### Configuration
Add to `.env`:
```env
# Email reminders (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

📖 **Full Documentation**: See [REMINDER_SYSTEM.md](REMINDER_SYSTEM.md)  
🧪 **Test Cases**: See [test_reminder_system.py](test_reminder_system.py)

---

## 🎯 Skill-Based Matching System

**Why Generic Ratings Suck:**
- ⚠️ Provider A: "4.8⭐" but only does plumbing repairs
- ⚠️ Provider B: "4.7⭐" but only does pipe installations
- ☹️ Customer books wrong provider for their specific need

**Our Solution: Expertise-Based Matching**
✅ **"Expert in AC gas refill"** - Show specific expertise  
✅ **"Top 5% in bathroom cleaning"** - Percentile rankings  
✅ **Skill-specific ratings** - Rate providers per-skill  
✅ **Smart matching** - Find experts for your exact needs  

### Key Features
- 🎯 Multi-skill provider matching
- 📊 Percentile rankings (Top X%)
- ✓ Admin-verified expertise
- ⭐ Skill-specific reviews
- 📈 Expertise trends & analytics
- 🏆 Expertise badges (🏆 Top 5%, ⭐ Top 10%, etc.)

### Quick Start
```python
# 1. Customer selects required skills
skills = [1, 3]  # [AC repair, cooling install]

# 2. System finds best providers
GET /api/skills/match?skills=1,3&limit=10

# 3. Returns ranked providers with:
[
  {
    "provider_name": "AC Experts Ltd",
    "match_score": 87.5,
    "expertise_labels": [
      "🏆 Top 5% in AC gas refill",
      "⭐ Top 10% in cooling installation"
    ]
  }
]

# 4. Customer books with confidence!
```

📖 **Full Documentation**: See [SKILL_BASED_MATCHING.md](SKILL_BASED_MATCHING.md)

---

## 🗄 Database Schema

```
users ──────────── service_providers ──── services
  │                                        │
  ├── bookings ──── payments               │
  │      │                                 │
  └── reviews ─────────────────────────────┘
       categories ──── services
```

**7 tables**: users, service_providers, categories, services, bookings, payments, reviews

---

## 📧 Email Notifications

Configure SMTP in `backend/.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Supports: booking confirmation, booking reminders.

---

## 📄 License

MIT — free for personal and commercial use.
