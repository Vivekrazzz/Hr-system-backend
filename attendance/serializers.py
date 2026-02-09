from rest_framework import serializers
from .models import Attendance
from tasks.serializers import TaskSerializer, MongoPrimaryKeyRelatedField
from authentication.models import User

from authentication.serializers import UserSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    employee_details = UserSerializer(source='employee', read_only=True)
    employee = serializers.CharField(source='employee.pk', read_only=True)
    total_duration_display = serializers.SerializerMethodField()
    entries = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = ('id', 'employee', 'employee_details', 'date', 'entries', 'total_hours', 'total_duration_display')

    def get_entries(self, obj):
        from django.utils import timezone
        import pytz
        # Ensure datetimes are serialized to strings in local timezone
        serialized = []
        for entry in obj.entries:
            e = entry.copy() if isinstance(entry, dict) else {}
            for key, value in e.items():
                if hasattr(value, 'isoformat'):
                    # If naive, assume it's UTC (Django's default storage)
                    if timezone.is_naive(value):
                        value = pytz.UTC.localize(value)
                    # Convert to local timezone before serializing
                    local_time = timezone.localtime(value)
                    e[key] = local_time.isoformat()
            serialized.append(e)
        return serialized

    def get_total_duration_display(self, obj):
        if obj.total_hours:
            hours = int(obj.total_hours)
            minutes = int((obj.total_hours - hours) * 60)
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "0m"
