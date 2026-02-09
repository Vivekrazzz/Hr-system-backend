import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

def test_auth():
    try:
        user = User.objects.first()
        if not user:
            print("No users found")
            return
            
        print(f"Testing auth for user: {user.email}")
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        print(f"Generated Token Sample: {token[:20]}...")
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Test an endpoint that requires authentication
        response = client.get('/api/auth/me/')
        print(f"Auth Test Status Code: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Auth Test Response: {response.data}")
        else:
            print(f"Auth Test Response: {response.content.decode()}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
