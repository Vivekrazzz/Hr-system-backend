import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication

try:
    user = User.objects.get(email='admin@example.com')
    print(f"User: {user.email}, _id: {user._id}")
    
    token = AccessToken.for_user(user)
    print(f"Token payload: {token.payload}")
    
    # Simulate authentication
    auth = JWTAuthentication()
    validated_token = auth.get_validated_token(str(token))
    
    print(f"Validated token ID: {validated_token['user_id']}")
    
    try:
        authenticated_user = auth.get_user(validated_token)
        print(f"SUCCESS: Authenticated as {authenticated_user.email}")
    except Exception as e:
        print(f"FAIL: Authentication failed during user lookup: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    import traceback
    traceback.print_exc()
