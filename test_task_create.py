import os
import django
import requests
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Login as admin
token_resp = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'email': 'admin@example.com', 
    'password': 'admin123'
})
token = token_resp.json()['access']

# Create task
deadline = (datetime.now() + timedelta(days=7)).isoformat()
task_resp = requests.post(
    'http://127.0.0.1:8000/api/tasks/assign/', 
    json={
        'title': 'Complete Project Report',
        'description': 'Prepare and submit the quarterly project report',
        'assigned_to': '6985dae69fee32e4bf553e9d',
        'deadline': deadline,
        'status': 'pending'
    },
    headers={'Authorization': f'Bearer {token}'}
)

print(f'Task creation status: {task_resp.status_code}')
if task_resp.status_code == 201:
    print('✅ Task created successfully!')
    print(f'Task data: {task_resp.json()}')
else:
    print(f'❌ Error: {task_resp.text}')
