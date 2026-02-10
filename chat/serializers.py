from rest_framework import serializers
from .models import Message
from authentication.serializers import UserSerializer
from authentication.models import User
from projects.models import Project
from tasks.models import Task
from bson import ObjectId

class MongoPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and len(data) == 24:
                oid = ObjectId(data)
            else:
                oid = data
            return self.get_queryset().get(pk=oid)
        except Exception as e:
            print(f"DEBUG: MongoPrimaryKeyRelatedField error: {e}")
            raise serializers.ValidationError(f"Invalid ID: {data}")

    def to_representation(self, value):
        if value is None:
            return None
        if hasattr(value, 'pk'):
            return str(value.pk)
        return str(value)

class MessageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    sender = serializers.CharField(source='sender._id', read_only=True)
    sender_details = UserSerializer(source='sender', read_only=True)
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()
    project = MongoPrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    task = MongoPrimaryKeyRelatedField(queryset=Task.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_details', 'sender_email', 'sender_name', 'content', 'timestamp', 'project', 'task']
        read_only_fields = ['id', 'sender', 'timestamp']

    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}"
        return ""

    def create(self, validated_data):
        return super().create(validated_data)
