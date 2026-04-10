#!/usr/bin/env python3
"""Test the authentication flow end-to-end."""
import requests
import sys
import time

base = 'http://127.0.0.1:8000/api'
unique_email = f'user_{int(time.time())}@example.com'

try:
    # Register
    print('=== REGISTER ===')
    reg_resp = requests.post(base + '/auth/register', json={
        'name': 'TestFlow User',
        'email': unique_email,
        'password': 'TestPass123',
        'role': 'customer'
    }, timeout=5)
    print(f'Status: {reg_resp.status_code}')
    
    if reg_resp.status_code in [201, 200]:
        user = reg_resp.json()
        print(f'✓ User created: id={user.get("id")}, email={user.get("email")}')
    else:
        print(f'✗ Registration failed: {reg_resp.text}')
        sys.exit(1)

    # Login
    print('\n=== LOGIN ===')
    login_resp = requests.post(base + '/auth/login', json={
        'email': unique_email,
        'password': 'TestPass123'
    }, timeout=5)
    print(f'Status: {login_resp.status_code}')
    
    if login_resp.status_code == 200:
        token_data = login_resp.json()
        token = token_data.get('access_token')
        token_type = token_data.get('token_type', 'bearer')
        print(f'✓ Login successful - token_type: {token_type}')
        print(f'  Token preview: {token[:50]}...')
    else:
        print(f'✗ Login failed: {login_resp.text}')
        sys.exit(1)

    # Get /auth/me
    print('\n=== AUTH/ME ===')
    me_resp = requests.get(base + '/auth/me', headers={
        'Authorization': f'{token_type} {token}'
    }, timeout=5)
    print(f'Status: {me_resp.status_code}')
    print(f'Response: {me_resp.text[:500]}')
    
    if me_resp.status_code == 200:
        print('✓ Auth/me successful!')
    else:
        print(f'✗ Auth/me failed with {me_resp.status_code}')

except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

