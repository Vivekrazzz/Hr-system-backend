import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from django.db import connection

try:
    print("Attempting to create user...")
    user = User.objects.create_user(email='test_final@example.com', password='password123', role='employee')
    print(f"User created: {user.email}")
except Exception:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(f"Exception Type: {exc_type}")
    print(f"Exception Value: {exc_value}")
    print("Full Traceback:")
    traceback.print_tb(exc_traceback)
    
    # Try to see last queries
    print("\nRecent Queries:")
    for query in connection.queries[-5:]:
        print(query)
