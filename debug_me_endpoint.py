import os
import django
import sys
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def test_me_endpoint():
    user = User.objects.filter(email='vivekrazzz111@gmail.com').first()
    if not user:
        print("User not found.")
        return

    print(f"Testing /api/auth/me/ for user: {user.email}")
    client = APIClient()
    
    # We can use force_authenticate to skip the actual JWT header parsing for now
    # to see if the view itself crashes, or we can simulate the whole flow.
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    try:
        response = client.get('/api/auth/me/')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print("Response Data (Error):", response.data if hasattr(response, 'data') else response.content)
        else:
            print("Response Data:", response.data)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_me_endpoint()
