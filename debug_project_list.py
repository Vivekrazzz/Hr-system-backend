import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project, ProjectMember
from authentication.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from projects.views import ProjectViewSet

def test_list_projects():
    try:
        user = User.objects.filter(role='admin').first()
        if not user:
            user = User.objects.first()
        
        print(f"Testing List as user: {user.email}")
        
        factory = APIRequestFactory()
        request = factory.get('/api/projects/projects/')
        force_authenticate(request, user=user)
        
        view = ProjectViewSet.as_view({'get': 'list'})
        response = view(request)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response Data: {response.data}")
        else:
            print(f"Success! Found {len(response.data)} projects.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_projects()
