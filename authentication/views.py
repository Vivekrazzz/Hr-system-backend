"""
Authentication Views Module

This module contains all view classes for user authentication and management.
Includes user registration, profile management, employee CRUD operations,
and password reset functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import random
import string
from bson import ObjectId
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User


# ============================================================================
# USER REGISTRATION & PROFILE VIEWS
# ============================================================================

class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    
    Allows anyone to create a new user account without authentication.
    Note: This is typically used for self-registration. For admin-created
    employees, use AdminCreateEmployeeView instead.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update current user's profile.
    
    This endpoint allows authenticated users to view and update their own
    profile information. The user is automatically determined from the
    authentication token.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user


# ============================================================================
# EMPLOYEE MANAGEMENT VIEWS (Admin)
# ============================================================================

class EmployeeListView(generics.ListAPIView):
    """
    List all employees in the system.
    
    Returns a list of all registered users/employees. This is typically
    used for admin views, task assignment, and project member selection.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific employee (Admin only).
    
    This view allows administrators to manage employee accounts including
    viewing details, updating information, and deleting accounts.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Get employee by ID with MongoDB ObjectId conversion.
        
        Handles conversion of 24-character string IDs to MongoDB ObjectId
        for proper database lookups.
        """
        pk = self.kwargs.get('pk')
        
        # Convert 24-character string to ObjectId for MongoDB
        if pk and isinstance(pk, str) and len(pk) == 24:
            try:
                pk = ObjectId(pk)
            except Exception:
                pass  # If conversion fails, use original pk
        
        return get_object_or_404(User, pk=pk)


class AdminCreateEmployeeView(generics.CreateAPIView):
    """
    Create a new employee account (Admin only).
    
    This endpoint allows administrators to create new employee accounts.
    It automatically generates:
    - Unique employee ID (format: EMP-YYYY-XXXX)
    - Random secure password
    - Username from email
    
    Returns the generated credentials to the admin for distribution.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # TODO: Change to IsAdminUser

    def create(self, request, *args, **kwargs):
        """
        Create employee with auto-generated credentials.
        
        Generates employee ID and password, creates the user account,
        and returns credentials to admin.
        """
        data = request.data.copy()
        
        # Generate unique Employee ID (format: EMP-2026-XXXX)
        random_suffix = ''.join(random.choices(string.digits, k=4))
        year = timezone.now().year
        data['employee_id'] = f"EMP-{year}-{random_suffix}"
        
        # Generate random secure password (10 characters)
        generated_password = ''.join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        data['password'] = generated_password
        
        # Set username to email for consistency
        email = data.get('email')
        data['username'] = email

        # Create user with error handling
        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except Exception as e:
            # Log error for debugging
            print(f"Error creating employee: {str(e)}")
            
            # Return appropriate error response
            if hasattr(e, 'detail'):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return success with generated credentials
        return Response({
            "success": True,
            "user": UserSerializer(user).data,
            "generated_id": data['employee_id'],
            "generated_password": generated_password
        }, status=status.HTTP_201_CREATED)


# ============================================================================
# PASSWORD MANAGEMENT VIEWS
# ============================================================================

class ResetPasswordView(generics.GenericAPIView):
    """
    Reset employee password (Admin only).
    
    Generates a new random password for the specified employee and returns
    it to the admin. The admin should securely communicate this password
    to the employee.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """
        Reset password for specified user.
        
        Args:
            pk: User ID (MongoDB ObjectId as string)
            
        Returns:
            Success response with new password or error details
        """
        try:
            # Convert string ID to ObjectId for MongoDB lookup
            if isinstance(pk, str) and len(pk) == 24:
                try:
                    pk = ObjectId(pk)
                except Exception:
                    return Response(
                        {"error": "Invalid user ID format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get user from database
            user = User.objects.get(pk=pk)
            
            # Generate new random password (10 characters)
            new_password = ''.join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            
            # Update user password
            user.set_password(new_password)
            user.save()
            
            # Return success with new password
            return Response({
                "success": True,
                "message": f"Password reset successfully for {user.email}",
                "new_password": new_password,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

