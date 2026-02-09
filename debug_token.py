import os
import django
import json
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    user = User.objects.get(email='admin@example.com')
    print(f"User: {user.email}, PK: {user.pk}")
    refresh = RefreshToken.for_user(user)
    print("Token created successfully")
    print(f"Access token: {refresh.access_token}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
