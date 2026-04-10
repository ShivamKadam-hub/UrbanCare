from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models.models import *  # noqa – ensure all models are registered
from app.routers import auth, services, bookings, payments, reviews, admin

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UrbanCare API",
    description="Full-stack service marketplace API — similar to Urban Company",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(reviews.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Welcome to UrbanCare API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
