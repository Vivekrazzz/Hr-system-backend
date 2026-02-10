from django.db import models
from django.conf import settings
from djongo import models as mongo_models
from django.utils import timezone

class Attendance(models.Model):
    _id = mongo_models.ObjectIdField(primary_key=True)
    @property
    def id(self):
        return self._id
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_attendances')
    date = models.DateField(default=timezone.now)
    entries = mongo_models.JSONField(default=list)
    total_hours = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('employee', 'date')

    def calculate_total_hours(self):
        from dateutil import parser
        from django.utils import timezone
        total_seconds = 0
        for entry in self.entries:
            if isinstance(entry, dict):
                ci = entry.get('check_in')
                co = entry.get('check_out')
                
                if isinstance(ci, str): ci = parser.isoparse(ci)
                if isinstance(co, str): co = parser.isoparse(co)
                
                if ci and co:
                    # Ensure both are aware for comparison
                    if timezone.is_naive(ci): ci = timezone.make_aware(ci)
                    if timezone.is_naive(co): co = timezone.make_aware(co)
                    total_seconds += (co - ci).total_seconds()
        self.total_hours = round(total_seconds / 3600, 2)
        return self.total_hours

    def __str__(self):
        return f"{self.employee.email} - {self.date}"

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('vacation', 'Vacation'),
        ('emergency', 'Emergency Leave'),
        ('other', 'Other'),
    ]

    _id = mongo_models.ObjectIdField(primary_key=True)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinate_leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='casual')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def id(self):
        return self._id

    def __str__(self):
        return f"{self.employee.email} ({self.start_date} to {self.end_date}) - {self.status}"
