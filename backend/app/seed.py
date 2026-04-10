"""
Seed script — populates the database with sample data for development.
Run: python -m app.seed
"""
from app.database import SessionLocal, engine, Base
from app.models.models import *
from app.utils.auth import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Clear existing data
    db.query(Review).delete()
    db.query(Payment).delete()
    db.query(Booking).delete()
    db.query(Service).delete()
    db.query(ServiceProvider).delete()
    db.query(User).delete()
    db.query(Category).delete()
    db.commit()

    # ── Admin ────────────────────────────────────────────────────────────
    admin = User(
        name="Admin",
        email="admin@urbancare.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(admin)

    # ── Categories ───────────────────────────────────────────────────────
    categories_data = [
        ("Cleaning", "cleaning", "🧹", "Professional home and office cleaning services"),
        ("Plumbing", "plumbing", "🔧", "Expert plumbing repair and installation"),
        ("Electrician", "electrician", "⚡", "Licensed electrical services"),
        ("Salon", "salon", "💇", "Haircut, styling, and beauty treatments"),
        ("Painting", "painting", "🎨", "Interior and exterior painting services"),
        ("Carpentry", "carpentry", "🪚", "Custom furniture and woodwork repairs"),
        ("Pest Control", "pest-control", "🐛", "Safe and effective pest removal"),
        ("Appliance Repair", "appliance-repair", "🔩", "All major appliance repairs"),
    ]
    categories = []
    for name, slug, icon, desc in categories_data:
        cat = Category(name=name, slug=slug, icon=icon, description=desc)
        db.add(cat)
        categories.append(cat)

    db.flush()

    # ── Sample Provider ──────────────────────────────────────────────────
    provider_user = User(
        name="Rajesh Kumar",
        email="provider@urbancare.com",
        password_hash=hash_password("provider123"),
        phone="+91-9876543210",
        role=UserRole.PROVIDER,
    )
    db.add(provider_user)
    db.flush()

    provider = ServiceProvider(
        user_id=provider_user.id,
        business_name="Rajesh Home Services",
        description="10+ years of experience in home maintenance and repair services.",
        experience_years=10,
        is_approved=True,
    )
    db.add(provider)
    db.flush()

    # ── Sample Services ──────────────────────────────────────────────────
    services_data = [
        (categories[0].id, "Deep Home Cleaning", "Complete deep cleaning for your home including kitchen, bathrooms, and living areas.", 1499, 180),
        (categories[0].id, "Office Cleaning", "Professional office and commercial space cleaning.", 2499, 240),
        (categories[1].id, "Pipe Leak Repair", "Quick and reliable pipe leak detection and repair.", 499, 60),
        (categories[1].id, "Bathroom Fitting", "Complete bathroom fixture installation.", 1999, 120),
        (categories[2].id, "Wiring & Rewiring", "Safe electrical wiring for homes and offices.", 799, 90),
        (categories[2].id, "Switchboard Repair", "Fix faulty switches and electrical panels.", 349, 45),
        (categories[3].id, "Haircut & Styling", "Professional haircut and styling at home.", 599, 60),
        (categories[3].id, "Bridal Makeup", "Premium bridal makeup package.", 4999, 180),
        (categories[4].id, "Room Painting", "Full room painting with premium paints.", 3999, 480),
        (categories[5].id, "Furniture Assembly", "Assembly and installation of flat-pack furniture.", 699, 120),
        (categories[6].id, "General Pest Control", "Complete pest control treatment for your home.", 1299, 120),
        (categories[7].id, "AC Service & Repair", "Air conditioner servicing and repair.", 899, 90),
    ]
    for cat_id, title, desc, price, dur in services_data:
        svc = Service(
            provider_id=provider.id,
            category_id=cat_id,
            title=title,
            description=desc,
            price=price,
            duration_minutes=dur,
        )
        db.add(svc)

    # ── Sample Customer ──────────────────────────────────────────────────
    customer = User(
        name="Priya Sharma",
        email="customer@urbancare.com",
        password_hash=hash_password("customer123"),
        phone="+91-9123456789",
        role=UserRole.CUSTOMER,
    )
    db.add(customer)

    db.commit()
    db.close()
    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()
