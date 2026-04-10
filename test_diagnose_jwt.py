#!/usr/bin/env python3
"""Diagnostic: decode and validate JWT locally."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import time
from jose import jwt, JWTError

from app.config import settings
from app.models.models import User
from app.database import SessionLocal

base = 'http://127.0.0.1:8000/api'
unique_email = f'user_{int(time.time())}@example.com'

# Register
reg_resp = requests.post(base + '/auth/register', json={
    'name': 'Diag User',
    'email': unique_email,
    'password': 'TestPass123',
    'role': 'customer'
}, timeout=5)
user_id = reg_resp.json()['id']
print(f'✓ Registered user id={user_id}')

# Login
login_resp = requests.post(base + '/auth/login', json={
    'email': unique_email,
    'password': 'TestPass123'
}, timeout=5)
token = login_resp.json()['access_token']
print(f'✓ Got token: {token[:50]}...')

# Decode JWT
print(f'\n=== JWT DECODING ===')
print(f'SECRET_KEY: {settings.SECRET_KEY}')
print(f'ALGORITHM: {settings.ALGORITHM}')

try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f'✓ JWT decoded successfully!')
    print(f'  Payload: {payload}')
    decoded_sub = payload.get('sub')
    print(f'  user_id from token (sub): {decoded_sub}')
except JWTError as e:
    print(f'✗ JWT decode failed: {e}')
    sys.exit(1)

# Query the database directly
print(f'\n=== DATABASE LOOKUP ===')
db = SessionLocal()
try:
    user = db.query(User).filter(User.id == decoded_sub).first()
    if user:
        print(f'✓ User found in DB: id={user.id}, email={user.email}, is_active={user.is_active}')
    else:
        print(f'✗ User NOT found in DB for id={decoded_sub}')
finally:
    db.close()

# List all users
print(f'\n=== ALL USERS IN DB ===')
db = SessionLocal()
try:
    all_users = db.query(User).all()
    print(f'Total users: {len(all_users)}')
    for u in all_users:
        print(f'  - id={u.id}, email={u.email}, is_active={u.is_active}')
finally:
    db.close()
