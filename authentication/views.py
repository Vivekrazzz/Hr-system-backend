from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .models import User

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

import random
import string
from django.utils import timezone

class EmployeeListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        return get_object_or_404(User, pk=pk)

    def perform_update(self, serializer):
        serializer.save()

class AdminCreateEmployeeView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Should be IsAdminUser

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        # 1. Generate unique Employee ID (e.g., EMP-2026-XXXX)
        random_suffix = ''.join(random.choices(string.digits, k=4))
        year = timezone.now().year
        data['employee_id'] = f"EMP-{year}-{random_suffix}"
        
        # 2. Generate random password
        generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        data['password'] = generated_password
        
        # 3. Handle email/username
        email = data.get('email')
        data['username'] = email

        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except Exception as e:
            print(f"Error creating employee: {str(e)}")
            if hasattr(e, 'detail'):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the generated credentials to the admin
        return Response({
            "success": True,
            "user": UserSerializer(user).data,
            "generated_id": data['employee_id'],
            "generated_password": generated_password
        }, status=status.HTTP_201_CREATED)

class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            from bson import ObjectId
            
            # Convert string ID to ObjectId for MongoDB lookup
            if isinstance(pk, str) and len(pk) == 24:
                try:
                    pk = ObjectId(pk)
                except:
                    return Response({
                        "error": "Invalid user ID format"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(pk=pk)
            
            # Generate new random password
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Set the new password
            user.set_password(new_password)
            user.save()
            
            return Response({
                "success": True,
                "message": f"Password reset successfully for {user.email}",
                "new_password": new_password,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
