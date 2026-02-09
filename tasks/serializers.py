from rest_framework import serializers
from .models import Task, TimeLog
from authentication.serializers import UserSerializer
from authentication.models import User
from bson import ObjectId

class MongoPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom field to handle MongoDB ObjectId conversion.
    Input: String ID -> ObjectId -> Target instance
    Output: Target instance/ObjectId -> String ID
    """
    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and len(data) == 24:
                oid = ObjectId(data)
            else:
                oid = data
            return self.get_queryset().get(pk=oid)
        except Exception:
            raise serializers.ValidationError(f"Invalid ID: {data}")

    def to_representation(self, value):
        if hasattr(value, 'pk'):
            return str(value.pk)
        return str(value)

class TaskSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    assigned_members_details = UserSerializer(source='assigned_members', many=True, read_only=True)
    assigned_members = MongoPrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    assigned_members_names = serializers.SerializerMethodField()
    project = MongoPrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'

    def to_internal_value(self, data):
        print(f"DEBUG: TaskSerializer received: {data}", flush=True)
        data_copy = data.copy() if hasattr(data, 'copy') else data
        
        # Format deadline
        if 'deadline' in data_copy:
            val = data_copy['deadline']
            if val == "" or val is None:
                data_copy['deadline'] = None
            elif isinstance(val, str):
                val = val.strip()
                if len(val) == 10:
                    data_copy['deadline'] = f"{val}T00:00:00Z"
                elif "T" in val and len(val) == 16:
                    data_copy['deadline'] = f"{val}:00Z"
                elif "T" in val and len(val) == 19:
                    data_copy['deadline'] = f"{val}Z"

        # Handle assigned_members if passed as single value or comma-separated string
        if 'assigned_members' in data_copy:
            val = data_copy['assigned_members']
            if isinstance(val, str):
                if val.strip() == "":
                    data_copy['assigned_members'] = []
                elif "," in val:
                    data_copy['assigned_members'] = [v.strip() for v in val.split(",") if v.strip()]
                else:
                    data_copy['assigned_members'] = [val.strip()]
            elif val is None:
                data_copy['assigned_members'] = []

        print(f"DEBUG: TaskSerializer modified to: {data_copy}", flush=True)
        return super().to_internal_value(data_copy)

    def get_assigned_members_names(self, obj):
        return [f"{u.first_name} {u.last_name}" for u in obj.assigned_members.all()]


class TimeLogSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    employee = MongoPrimaryKeyRelatedField(queryset=User.objects.all())
    employee_details = UserSerializer(source='employee', read_only=True)
    task = MongoPrimaryKeyRelatedField(queryset=Task.objects.all())
    task_details = TaskSerializer(source='task', read_only=True)
    
    class Meta:
        model = TimeLog
        fields = ['id', 'employee', 'employee_details', 'task', 'task_details', 'date', 'hours', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_internal_value(self, data):
        data_copy = data.copy() if hasattr(data, 'copy') else data
        
        # Format date if needed
        if 'date' in data_copy and data_copy['date'] == "":
            data_copy['date'] = None
            
        return super().to_internal_value(data_copy)

    def validate(self, data):
        """
        Validate that total hours for a day don't exceed 24 hours
        """
        from django.db.models import Sum
        
        employee = data.get('employee') or self.context['request'].user
        date = data.get('date')
        hours = data.get('hours')
        
        if date and hours:
            # Get existing hours for this date (excluding current record if updating)
            existing_logs = TimeLog.objects.filter(employee=employee, date=date)
            
            # If updating, exclude the current log
            if self.instance:
                existing_logs = existing_logs.exclude(pk=self.instance.pk)
            
            total_existing_hours = existing_logs.aggregate(total=Sum('hours'))['total'] or 0
            total_hours = float(total_existing_hours) + float(hours)
            
            if total_hours > 24:
                raise serializers.ValidationError({
                    'hours': f'Total hours for {date} would be {total_hours:.2f}h. Cannot exceed 24 hours per day. You already have {total_existing_hours:.2f}h logged.'
                })
        
        return data

