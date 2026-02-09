import os
import django
import traceback
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User

try:
    print("Attempting to create user...")
    user = User.objects.create_user(email='test2@example.com', password='password123', role='employee')
    print(f"User created successfully: {user.email} with ID {user.pk}")
except Exception as e:
    print(f"Type: {type(e)}")
    print(f"Error: {e}")
    if hasattr(e, '__cause__') and e.__cause__:
        print(f"Cause: {e.__cause__}")
    traceback.print_exc()
