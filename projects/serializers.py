from rest_framework import serializers
from .models import Project, ProjectMember
from authentication.models import User
from authentication.serializers import UserSerializer
from bson import ObjectId

class MongoPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and len(data) == 24:
                oid = ObjectId(data)
            else:
                oid = data
            return self.get_queryset().get(pk=oid)
        except (User.DoesNotExist, Project.DoesNotExist, Exception):
            if self.queryset and self.queryset.model == User:
                 raise serializers.ValidationError(f"Invalid User ID: {data}")
            raise serializers.ValidationError(f"Invalid ID: {data}")

    def to_representation(self, value):
        if hasattr(value, 'pk'):
            return str(value.pk)
        return str(value)

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    invited_by_details = UserSerializer(source='invited_by', read_only=True)
    id = serializers.CharField(read_only=True)
    user = MongoPrimaryKeyRelatedField(queryset=User.objects.all())
    project = MongoPrimaryKeyRelatedField(queryset=Project.objects.all())
    invited_by = MongoPrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'user_details', 'status', 'role', 'invited_by', 'invited_by_details', 'joined_at']
        read_only_fields = ['status', 'invited_by', 'joined_at']

class ProjectSerializer(serializers.ModelSerializer):
    members = ProjectMemberSerializer(many=True, read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    created_by = MongoPrimaryKeyRelatedField(read_only=True)
    id = serializers.CharField(read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'company_name', 'description', 'status', 'created_by', 'created_by_details', 'created_at', 'updated_at', 'members', 'progress']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_progress(self, obj):
        total_tasks = obj.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = obj.tasks.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 2)

class ProjectInvitationSerializer(serializers.ModelSerializer):
    user = MongoPrimaryKeyRelatedField(queryset=User.objects.all())
    project = MongoPrimaryKeyRelatedField(queryset=Project.objects.all())
    
    class Meta:
        model = ProjectMember
        fields = ['project', 'user', 'role']
