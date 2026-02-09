import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import authenticate
user = authenticate(email='admin@example.com', password='admin123')
if user:
    print(f"SUCCESS: Authenticated as {user.email}")
else:
    print("FAIL: Authentication failed")
