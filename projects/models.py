from django.db import models
from django.conf import settings
from djongo import models as mongo_models

class Project(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=(
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ), default='ongoing')

    @property
    def id(self):
        return self._id

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)
    @property
    def id(self):
        return self._id
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ), default='pending')
    role = models.CharField(max_length=50, default='member')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations', null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.email} in {self.project.name} ({self.status})"
