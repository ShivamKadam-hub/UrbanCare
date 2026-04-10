# UrbanCare — Home Services Marketplace

A full-stack web application similar to Urban Company, built with **FastAPI**, **React**, **PostgreSQL**, **JWT authentication**, and **Docker**.

---

## ✨ Features

### Customer
- Register/Login with JWT • Browse & search services • Filter by category
- Book appointments with date/time slots • Online payment (simulated)
- View booking history • Rate & review service providers

### Service Provider
- Register as provider • Add/manage services offered
- Accept/reject booking requests • Mark bookings complete
- View earnings dashboard

### Admin
- Manage users & providers • Approve provider registrations
- CRUD categories & services • Analytics dashboard with charts
- View all bookings

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
│   │   ├── models/models.py   # ORM models (7 tables)
│   │   ├── schemas/schemas.py # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py        # /api/auth/*
│   │   │   ├── services.py    # /api/services/*
│   │   │   ├── bookings.py    # /api/bookings/*
│   │   │   ├── payments.py    # /api/payments/*
│   │   │   ├── reviews.py     # /api/reviews/*
│   │   │   └── admin.py       # /api/admin/*
│   │   └── utils/
│   │       ├── auth.py        # JWT + password hashing
│   │       └── email.py       # Email notifications
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/client.js      # Axios + JWT interceptor
│   │   ├── context/AuthContext.jsx
│   │   ├── components/        # Navbar, Footer, ServiceCard
│   │   ├── pages/             # 9 page components
│   │   ├── App.jsx            # Router
│   │   ├── App.css            # Component styles
│   │   ├── index.css          # Design system
│   │   └── main.jsx           # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
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
