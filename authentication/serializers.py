from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        
        # Ensure user_id is string (fixes ObjectId not JSON serializable error)
        # The key 'user_id' comes from SIMPLE_JWT settings (default claim)
        # If USER_ID_FIELD is '_id', the value is an ObjectId, which breaks JSON serialization
        if '_id' in token:
            token['_id'] = str(token['_id'])
        if 'user_id' in token:
            token['user_id'] = str(token['user_id'])
            
        return token

class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    manager = serializers.SerializerMethodField()
    manager_details = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'employee_id', 
                  'phone', 'department', 'designation', 'date_of_joining', 'password', 'avatar', 'manager', 'manager_details')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True}
        }

    def get_manager(self, obj):
        if obj.manager:
            return str(obj.manager._id)
        return None

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
