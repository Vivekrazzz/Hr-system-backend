import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project, ProjectMember
from projects.serializers import ProjectSerializer
from authentication.models import User
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def test_serialization():
    try:
        projects = Project.objects.all()
        print(f"Found {projects.count()} projects.")
        
        factory = APIRequestFactory()
        request = factory.get('/')
        
        for p in projects:
            try:
                print(f"Serializing project: {p.name} ({p.pk})")
                serializer = ProjectSerializer(p, context={'request': Request(request)})
                data = serializer.data
                # print(f"  Success: {data['name']}")
            except Exception as e:
                print(f"  FAILED to serialize {p.pk}: {str(e)}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serialization()
