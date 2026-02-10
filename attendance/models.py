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
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        total_seconds = 0
        for entry in self.entries:
            if isinstance(entry, dict):
                ci = entry.get('check_in')
                co = entry.get('check_out')
                
                if isinstance(ci, str): ci = parse_datetime(ci)
                if isinstance(co, str): co = parse_datetime(co)
                
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
    _id = mongo_models.ObjectIdField(primary_key=True)
    @property
    def id(self):
        return self._id
        
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    LEAVE_TYPES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('vacation', 'Vacation'),
        ('other', 'Other'),
    )

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='casual')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    
    # Who approved/rejected it
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='processed_leaves'
    )
    process_note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.email} - {self.leave_type} ({self.status})"
