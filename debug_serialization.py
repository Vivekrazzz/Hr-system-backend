import os
import django
import sys

# Append current directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from authentication.serializers import UserSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def test_serialization():
    user = User.objects.filter(email='vivekrazzz111@gmail.com').first()
    if not user:
        user = User.objects.all().first()
        if not user:
            print("No users found in database.")
            return

    print(f"Testing for user: {user.email}")
    
    # Simulate a request for serializer context
    factory = APIRequestFactory()
    request = factory.get('/')
    
    serializer = UserSerializer(user, context={'request': request})
    try:
        data = serializer.data
        print("Serialization successful!")
        print("Data keys:", list(data.keys()))
        print("Avatar URL:", data.get('avatar'))
    except Exception as e:
        import traceback
        print("Serialization FAILED:")
        traceback.print_exc()

if __name__ == "__main__":
    test_serialization()
