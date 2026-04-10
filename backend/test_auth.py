import sys
import os

# add backend dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import User
from app.utils.auth import hash_password, verify_password

def test_auth():
    db = SessionLocal()
    email = "test_auth_script@example.com"
    password = "MySecurePassword123!"
    
    # Check if user exists, delete if so
    user = db.query(User).filter(User.email == email).first()
    if user:
        db.delete(user)
        db.commit()

    # Register
    hashed_pw = hash_password(password)
    print("Hashed PW length:", len(hashed_pw))
    print("Hashed PW:", hashed_pw)
    
    new_user = User(
        name="Test Auth Script",
        email=email,
        password_hash=hashed_pw,
        role="customer"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print("User registered with ID:", new_user.id)
    
    # Login
    login_user = db.query(User).filter(User.email == email).first()
    if not login_user:
        print("Login failed: User not found!")
        return

    is_valid = verify_password(password, login_user.password_hash)
    print("Is password valid?:", is_valid)
    
    db.delete(login_user)
    db.commit()

if __name__ == "__main__":
    test_auth()
