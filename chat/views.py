from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer
from projects.models import Project, ProjectMember
from tasks.models import Task
from rest_framework.exceptions import PermissionDenied, ValidationError
from bson import ObjectId

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_param = self.request.query_params.get('project')
        task_param = self.request.query_params.get('task')

        if task_param:
            try:
                task_id = ObjectId(task_param) if isinstance(task_param, str) and len(task_param) == 24 else task_param
                task = Task.objects.get(_id=task_id)
                
                is_assigned = task.assigned_members.filter(_id=user._id).exists()
                is_admin = user.role == 'admin'
                is_project_creator = task.project and task.project.created_by == user

                if not (is_assigned or is_admin or is_project_creator):
                    return Message.objects.none()
                
                return Message.objects.filter(task_id=task_id)
            except Exception:
                return Message.objects.none()

        if project_param:
            try:
                project_id = ObjectId(project_param) if isinstance(project_param, str) and len(project_param) == 24 else project_param
                
                # Check membership
                is_member = ProjectMember.objects.filter(project_id=project_id, user=user, status='accepted').exists()
                is_admin = user.role == 'admin'
                is_creator = Project.objects.filter(_id=project_id, created_by=user).exists()

                if not (is_member or is_admin or is_creator):
                    return Message.objects.none()
                
                # Return only group messages (where task is null)
                return Message.objects.filter(project_id=project_id, task__isnull=True)
            except Exception:
                return Message.objects.none()

        return Message.objects.filter(sender=user)

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')
        task = serializer.validated_data.get('task')

        if task:
            is_assigned = task.assigned_members.filter(_id=user._id).exists()
            is_admin = user.role == 'admin'
            is_project_creator = task.project and task.project.created_by == user

            if not (is_assigned or is_admin or is_project_creator):
                raise PermissionDenied("You are not authorized to chat in this task.")
            
            # Ensure the project field is set if the task belongs to a project
            if not project and task.project:
                serializer.save(sender=user, project=task.project)
                return

        elif project:
            is_member = ProjectMember.objects.filter(project=project, user=user, status='accepted').exists()
            is_admin = user.role == 'admin'
            is_creator = project.created_by == user

            if not (is_member or is_admin or is_creator):
                raise PermissionDenied("You are not authorized to chat in this project.")

        serializer.save(sender=user)
