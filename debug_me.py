import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from authentication.views import UserDetailView
from rest_framework.test import APIRequestFactory, force_authenticate

try:
    user = User.objects.get(email='admin@example.com')
    print(f"User: {user.email}, ID: {user.id}, PK: {user.pk}")
    
    factory = APIRequestFactory()
    request = factory.get('/api/auth/me/')
    force_authenticate(request, user=user)
    
    view = UserDetailView.as_view()
    response = view(request)
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
