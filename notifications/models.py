from django.db import models
from django.conf import settings
from djongo import models as mongo_models
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('leave_request', 'New Leave Request'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('project_invite', 'Project Invitation'),
        ('task_assigned', 'Task Assigned'),
        ('chat_message', 'New Message'),
        ('announcement', 'System Announcement'),
    ]

    _id = mongo_models.ObjectIdField(primary_key=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_id = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def id(self):
        return self._id

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.title} ({self.notification_type})"
