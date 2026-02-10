from rest_framework import serializers
from .models import User
from bson import ObjectId

class MongoPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
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

class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    manager = MongoPrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    manager_details = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'employee_id', 
                  'phone', 'department', 'designation', 'date_of_joining', 'password', 'avatar', 'manager', 'manager_details')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True}
        }

    def get_manager_details(self, obj):
        if obj.manager:
            return {
                'id': str(obj.manager._id),
                'first_name': obj.manager.first_name,
                'last_name': obj.manager.last_name,
                'email': obj.manager.email
            }
        return None

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password', None)
        # Remove username if present to avoid multiple value error
        if 'username' in validated_data:
            validated_data.pop('username')
            
        user = User.objects.create_user(email, password, **validated_data)
        return user

    def to_internal_value(self, data):
        # Convert empty strings to None for fields that expect specific types (like Date)
        # to avoid "Date has wrong format" errors before validation.
        data_copy = data.copy() if hasattr(data, 'copy') else data
        for field in ['date_of_joining']:
            if field in data_copy and data_copy[field] == "":
                data_copy[field] = None
        return super().to_internal_value(data_copy)

    def update(self, instance, validated_data):
        # Handle password separately in the view or here
        password = validated_data.pop('password', None)
        
        # Sync username if email changes
        if 'email' in validated_data:
            validated_data['username'] = validated_data['email']
            
        # Clean empty strings to None for optional fields
        for field in ['phone', 'department', 'designation', 'date_of_joining', 'employee_id']:
            if field in validated_data and validated_data[field] == "":
                validated_data[field] = None

        instance = super().update(instance, validated_data)
        
        if password:
            instance.set_password(password)
            instance.save()
            
        return instance
