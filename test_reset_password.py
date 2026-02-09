import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Login as admin
token_resp = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'email': 'admin@example.com', 'password': 'admin123'})
token = token_resp.json()['access']

# Reset password for test5
reset_resp = requests.post(
    'http://127.0.0.1:8000/api/auth/employees/6985dae69fee32e4bf553e9d/reset-password/', 
    headers={'Authorization': f'Bearer {token}'}
)
data = reset_resp.json()
print(f"Password reset successful!")
print(f"New password for test5@example.com: {data['new_password']}")

# Test login with new password
login_test = requests.post(
    'http://127.0.0.1:8000/api/auth/login/', 
    json={'email': 'test5@example.com', 'password': data['new_password']}
)
print(f"Login test with new password: {login_test.status_code} (200 = success)")
