from rest_framework import serializers
from .models import Notification
from authentication.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    sender_details = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'sender', 'sender_details', 
            'notification_type', 'title', 'message', 
            'related_id', 'is_read', 'created_at'
        )
        read_only_fields = ('recipient', 'sender', 'notification_type', 'title', 'message', 'related_id', 'created_at')
