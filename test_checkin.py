import requests

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# django.setup()

# Login as admin
token_resp = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'email': 'admin@example.com', 'password': 'admin123'})
token = token_resp.json()['access']

# Check-in
print("Attempting Check-in...")
checkin_resp = requests.post(
    'http://127.0.0.1:8000/api/attendance/checkin/', 
    json={
        'check_in_lat': 27.7,
        'check_in_lng': 85.3,
        'check_in_note': 'Office'
    },
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Check-in Status: {checkin_resp.status_code}")
print(f"Check-in Response: {checkin_resp.text}")

if checkin_resp.status_code == 201:
    print("✅ Check-in successful")
else:
    print("❌ Check-in failed")

# Cleanup: Check out immediately if successful to allow retry
if checkin_resp.status_code == 201:
    print("Attempting Cleanup Check-out...")
    checkout_resp = requests.patch(
        'http://127.0.0.1:8000/api/attendance/checkout/', 
        json={
            'check_out_lat': 27.7,
            'check_out_lng': 85.3,
            'check_out_note': 'Leaving'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"Cleanup Check-out Status: {checkout_resp.status_code}")
