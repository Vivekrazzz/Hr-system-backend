import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import User

@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    if old_user.avatar and old_user.avatar != instance.avatar:
        if os.path.isfile(old_user.avatar.path):
            os.remove(old_user.avatar.path)

@receiver(post_delete, sender=User)
def delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
