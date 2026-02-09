from django.db import models
from django.conf import settings
from djongo import models as mongo_models

class Task(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)

    @property
    def id(self):
        return self._id
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    assigned_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks')
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TimeLog(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)

    @property
    def id(self):
        return self._id

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_logs')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 2.5 hours
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.employee.email} - {self.task.title} - {self.hours}h on {self.date}"
