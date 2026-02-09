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

def test_create_project():
    try:
        user = User.objects.filter(role='admin').first()
        if not user:
            user = User.objects.first()
        
        print(f"Testing as user: {user.email}")
        
        factory = APIRequestFactory()
        data = {
            'name': 'Test Project',
            'company_name': 'Test Company',
            'description': 'Test Description'
        }
        request = factory.post('/api/projects/projects/', data, format='json')
        force_authenticate(request, user=user)
        
        view = ProjectViewSet.as_view({'post': 'create'})
        response = view(request)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_project()
