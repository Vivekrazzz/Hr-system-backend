from django.db import models
from django.conf import settings
from djongo import models as mongo_models
from projects.models import Project
from tasks.models import Task

class Message(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # can be linked to a project (group chat) or a task (task chat)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_messages', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_messages', null=True, blank=True)

    @property
    def id(self):
        return self._id

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        # Use email if available, otherwise just 'User'
        sender_label = getattr(self.sender, 'email', str(self.sender))
        return f"{sender_label}: {self.content[:20]}..."
