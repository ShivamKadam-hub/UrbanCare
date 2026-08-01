"""Add Stripe columns to payments table."""
from app.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'payments'"
        ))
        cols = [r[0] for r in result]
        print(f"Current columns: {cols}")

        # Add missing columns
        if 'stripe_session_id' not in cols:
            conn.execute(text("ALTER TABLE payments ADD COLUMN stripe_session_id VARCHAR(255)"))
            print("Added: stripe_session_id")
        else:
            print("Already exists: stripe_session_id")

        if 'stripe_payment_intent_id' not in cols:
            conn.execute(text("ALTER TABLE payments ADD COLUMN stripe_payment_intent_id VARCHAR(255)"))
            print("Added: stripe_payment_intent_id")
        else:
            print("Already exists: stripe_payment_intent_id")

        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
