import os
import django
import sys
from django.conf import settings
from djongo import models as mongo_models
from django.contrib.auth.models import AbstractUser

# Mock settings if needed or use existing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User as CurrentUser

print(f"Current PK field name: {CurrentUser._meta.pk.name}")
print(f"Current PK field column: {CurrentUser._meta.pk.db_column}")

try:
    u = CurrentUser.objects.get(email='admin@example.com')
    print(f"Found user: {u.email}")
    print(f"pk value: {u.pk}, type: {type(u.pk)}")
    
    # Try querying by string
    pk_str = str(u.pk)
    print(f"Querying by string: {pk_str}")
    try:
        u2 = CurrentUser.objects.get(pk=pk_str)
        print("SUCCESS: Found by string!")
    except CurrentUser.DoesNotExist:
        print("FAIL: DoesNotExist by string")
        
except Exception as e:
    print(f"Error: {e}")
