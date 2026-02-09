from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Task, TimeLog
from .serializers import TaskSerializer, TimeLogSerializer
from django.db.models import Sum
from datetime import datetime, timedelta

class MyTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_members=self.request.user)

class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all().order_by('-deadline')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

class AssignTaskView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        return get_object_or_404(Task, pk=pk)

class TaskDeleteView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        return get_object_or_404(Task, pk=pk)

class UpdateTaskView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try:
                pk = ObjectId(pk)
            except:
                pass
        
        return get_object_or_404(Task, pk=pk)

# TimeLog Views
class TimeLogListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Employees see only their own time logs
        # Admins see all time logs
        if self.request.user.role == 'admin':
            return TimeLog.objects.all()
        return TimeLog.objects.filter(employee=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign the current user as the employee
        serializer.save(employee=self.request.user)

class TimeLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Employees can only access their own time logs
        if self.request.user.role == 'admin':
            return TimeLog.objects.all()
        return TimeLog.objects.filter(employee=self.request.user)

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: 
                pk = ObjectId(pk)
            except: 
                pass
        return get_object_or_404(self.get_queryset(), pk=pk)

class MyTimeLogsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get query parameters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Base queryset
        queryset = TimeLog.objects.filter(employee=request.user)
        
        # Apply date filters
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Get total hours
        total_hours = queryset.aggregate(total=Sum('hours'))['total'] or 0
        
        # Serialize data
        serializer = TimeLogSerializer(queryset, many=True)
        
        return Response({
            'time_logs': serializer.data,
            'total_hours': float(total_hours),
            'count': queryset.count()
        })

