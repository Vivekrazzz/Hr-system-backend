"""
Task and Time Log Views Module

This module contains view classes for task management and time logging.
Includes task CRUD operations, assignment, and time tracking functionality.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from bson import ObjectId
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task, TimeLog
from .serializers import TaskSerializer, TimeLogSerializer


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_to_objectid(pk):
    """
    Convert string ID to MongoDB ObjectId if applicable.
    
    Args:
        pk: Primary key (string or ObjectId)
        
    Returns:
        ObjectId if conversion successful, otherwise original pk
    """
    if pk and isinstance(pk, str) and len(pk) == 24:
        try:
            return ObjectId(pk)
        except Exception:
            pass
    return pk


# ============================================================================
# TASK VIEWS
# ============================================================================

class MyTasksView(generics.ListAPIView):
    """
    List tasks assigned to the current user.
    
    Returns all tasks where the authenticated user is listed as an
    assigned member. Used for employee task dashboard.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tasks assigned to current user."""
        return Task.objects.filter(assigned_members=self.request.user)


class TaskListView(generics.ListAPIView):
    """
    List all tasks in the system (Admin view).
    
    Returns all tasks ordered by deadline (most urgent first).
    Typically used for admin dashboard and task overview.
    """
    queryset = Task.objects.all().order_by('-deadline')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssignTaskView(generics.CreateAPIView):
    """
    Create and assign a new task.
    
    Allows creating new tasks with title, description, deadline,
    priority, and assigned members.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific task.
    
    Provides full CRUD operations for individual tasks. Handles MongoDB
    ObjectId conversion for proper database lookups.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get task by ID with MongoDB ObjectId conversion."""
        pk = convert_to_objectid(self.kwargs.get('pk'))
        return get_object_or_404(Task, pk=pk)


# Note: TaskDeleteView and UpdateTaskView are redundant as TaskDetailView
# already provides delete and update functionality through
# RetrieveUpdateDestroyAPIView. Keeping them for backward compatibility.

class TaskDeleteView(generics.DestroyAPIView):
    """
    Delete a task (Legacy endpoint).
    
    Note: This is redundant with TaskDetailView's delete functionality.
    Kept for backward compatibility with existing frontend code.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get task by ID with MongoDB ObjectId conversion."""
        pk = convert_to_objectid(self.kwargs.get('pk'))
        return get_object_or_404(Task, pk=pk)


class UpdateTaskView(generics.UpdateAPIView):
    """
    Update a task (Legacy endpoint).
    
    Note: This is redundant with TaskDetailView's update functionality.
    Kept for backward compatibility with existing frontend code.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get task by ID with MongoDB ObjectId conversion."""
        pk = convert_to_objectid(self.kwargs.get('pk'))
        return get_object_or_404(Task, pk=pk)


# ============================================================================
# TIME LOG VIEWS
# ============================================================================

class TimeLogListCreateView(generics.ListCreateAPIView):
    """
    List and create time log entries.
    
    Employees can view and create their own time logs.
    Admins can view all time logs in the system.
    """
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return time logs based on user role.
        
        - Admins: See all time logs
        - Employees: See only their own time logs
        """
        if self.request.user.role == 'admin':
            return TimeLog.objects.all()
        return TimeLog.objects.filter(employee=self.request.user)

    def perform_create(self, serializer):
        """
        Create time log entry.
        
        Automatically assigns the current user as the employee for the
        time log entry to prevent users from logging time for others.
        """
        serializer.save(employee=self.request.user)


class TimeLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific time log entry.
    
    Employees can only access their own time logs.
    Admins can access all time logs.
    """
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return time logs based on user role.
        
        - Admins: See all time logs
        - Employees: See only their own time logs
        """
        if self.request.user.role == 'admin':
            return TimeLog.objects.all()
        return TimeLog.objects.filter(employee=self.request.user)

    def get_object(self):
        """Get time log by ID with MongoDB ObjectId conversion."""
        pk = convert_to_objectid(self.kwargs.get('pk'))
        return get_object_or_404(self.get_queryset(), pk=pk)


class MyTimeLogsView(APIView):
    """
    Get current user's time logs with optional date filtering.
    
    Supports filtering by date range and returns summary statistics
    including total hours logged and entry count.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieve time logs with optional date filtering.
        
        Query Parameters:
            date_from (str): Start date (YYYY-MM-DD)
            date_to (str): End date (YYYY-MM-DD)
            
        Returns:
            JSON response with time logs, total hours, and count
        """
        # Extract query parameters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Base queryset filtered to current user
        queryset = TimeLog.objects.filter(employee=request.user)
        
        # Apply date range filters if provided
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Calculate total hours logged
        total_hours = queryset.aggregate(total=Sum('hours'))['total'] or 0
        
        # Serialize time log data
        serializer = TimeLogSerializer(queryset, many=True)
        
        # Return response with data and statistics
        return Response({
            'time_logs': serializer.data,
            'total_hours': float(total_hours),
            'count': queryset.count()
        })
