import os
import django
from django.conf import settings

# Setup django
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from attendance.models import Attendance
from authentication.models import User

u = User.objects.first()
print(f"User PK: {u.pk} ({type(u.pk)})")

a = Attendance(employee=u)
a.save()
print(f"New Attendance ID (after save): {a.pk} ({type(a.pk)})")
