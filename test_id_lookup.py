import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from djongo import models as mongo_models
from django.contrib.auth.models import AbstractUser

class TempUser(AbstractUser):
    id = mongo_models.ObjectIdField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'authentication_user'

try:
    pk_str = '6985cdea692fd937a5dc6c2c'
    print(f"Testing TempUser lookup with id={pk_str}")
    # This will likely fail with DoesNotExist if it doesn't auto-convert
    try:
        u = TempUser.objects.get(id=pk_str)
        print("SUCCESS")
    except TempUser.DoesNotExist:
        print("FAIL (DoesNotExist)")
    except Exception as e:
        print(f"ERROR: {e}")
except Exception as e:
    import traceback
    traceback.print_exc()
