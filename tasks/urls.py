from django.urls import path
from .views import (
    MyTasksView, AssignTaskView, UpdateTaskView, TaskListView, 
    TaskDeleteView, TaskDetailView, TimeLogListCreateView, 
    TimeLogDetailView, MyTimeLogsView
)

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('my/', MyTasksView.as_view(), name='my_tasks'),
    path('assign/', AssignTaskView.as_view(), name='assign_task'),
    path('update/<str:pk>/', UpdateTaskView.as_view(), name='update_task'),
    path('delete/<str:pk>/', TaskDeleteView.as_view(), name='delete_task'),
    path('<str:pk>/', TaskDetailView.as_view(), name='task_detail'),
    
    # TimeLog endpoints
    path('timelogs/', TimeLogListCreateView.as_view(), name='timelog_list_create'),
    path('timelogs/my/', MyTimeLogsView.as_view(), name='my_timelogs'),
    path('timelogs/<str:pk>/', TimeLogDetailView.as_view(), name='timelog_detail'),
]

