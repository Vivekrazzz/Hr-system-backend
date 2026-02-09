import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User
from tasks.models import Task
from datetime import datetime, timedelta
from bson import ObjectId

try:
    # Get user
    user_id = ObjectId('6985dae69fee32e4bf553e9d')
    user = User.objects.get(pk=user_id)
    print(f"Found user: {user.email}")
    
    # Create task directly
    task = Task.objects.create(
        title='Test Task Direct',
        description='Testing direct creation',
        assigned_to=user,
        deadline=datetime.now() + timedelta(days=7),
        status='pending'
    )
    print(f"✅ Task created successfully! ID: {task.id}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
