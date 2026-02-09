import os
import django
from bson import ObjectId

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project, ProjectMember
from authentication.models import User

def debug_invite():
    try:
        project = Project.objects.first()
        user = User.objects.last()
        
        if not project or not user:
            print("Missing project or user")
            return
            
        print(f"Project ID: {project.pk} ({type(project.pk)})")
        print(f"User ID: {user.pk} ({type(user.pk)})")
        
        uid = str(user.pk)
        print(f"Attempting invite with string ID: {uid}")
        
        # Simulating logic in views.py
        exists = ProjectMember.objects.filter(project=project, user_id=uid).exists()
        print(f"Check exists(user_id=str): {exists}")
        
        exists_oid = ProjectMember.objects.filter(project=project, user_id=ObjectId(uid)).exists()
        print(f"Check exists(user_id=ObjectId): {exists_oid}")
        
        # Check if ProjectMember records use ObjectId
        pm = ProjectMember.objects.filter(project=project).first()
        if pm:
            print(f"Sample ProjectMember.user_id: {pm.user_id} ({type(pm.user_id)})")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_invite()
