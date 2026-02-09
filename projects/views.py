from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Project, ProjectMember
from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectInvitationSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Project.objects.none()
        
        # Admin can see all
        if getattr(user, 'role', 'employee') == 'admin':
            return Project.objects.all()
            
        # For employees, get projects they created or are members of
        # We manually combine and unique to avoid Djongo's distinct() issues
        created_projects = Project.objects.filter(created_by=user)
        membership_projects = Project.objects.filter(members__user=user)
        
        # Combine querysets using union or just return a list if DRF allows
        # In Djongo, sometimes it's safer to just return a combined list of IDs and then filter
        pks = set(list(created_projects.values_list('pk', flat=True)) + 
                  list(membership_projects.values_list('pk', flat=True)))
        
        return Project.objects.filter(pk__in=pks)

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        # Use get_queryset to ensure permission
        return get_object_or_404(self.get_queryset(), pk=pk)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        # Create a ProjectMember entry for the creator as 'accepted'
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            status='accepted',
            role='owner'
        )

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if project.created_by != request.user and getattr(request.user, 'role', 'employee') != 'admin':
            return Response({'error': 'You do not have permission to edit this project'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.created_by != request.user and getattr(request.user, 'role', 'employee') != 'admin':
            return Response({'error': 'You do not have permission to delete this project'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        from bson import ObjectId
        project = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        # Support single user_id for backward compatibility
        user_id = request.data.get('user_id')
        if user_id and not user_ids:
            user_ids = [user_id]
            
        role = request.data.get('role', 'member')
        
        if not user_ids:
            return Response({'error': 'user_ids or user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = {'sent': [], 'skipped': [], 'errors': []}
        
        for uid in user_ids:
            try:
                # Ensure we have an ObjectId for the user lookup
                if isinstance(uid, str) and len(uid) == 24:
                    target_oid = ObjectId(uid)
                else:
                    target_oid = uid
                
                # Use user_id=target_oid to ensure Djongo matches correctly
                if ProjectMember.objects.filter(project=project, user_id=target_oid).exists():
                    results['skipped'].append(str(uid))
                    continue
                    
                ProjectMember.objects.create(
                    project=project,
                    user_id=target_oid,
                    invited_by=request.user,
                    role=role,
                    status='pending'
                )
                results['sent'].append(str(uid))
            except Exception as e:
                results['errors'].append({'id': str(uid), 'error': str(e)})
            
        status_code = status.HTTP_201_CREATED if results['sent'] else status.HTTP_200_OK
        return Response({
            'message': f'Invitations processed. Sent: {len(results["sent"])}, Skipped: {len(results["skipped"])}',
            'results': results
        }, status=status_code)

    @action(detail=False, methods=['get'])
    def invitations(self, request):
        invites = ProjectMember.objects.filter(user=request.user, status='pending')
        serializer = ProjectMemberSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def tasks(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            tasks = Task.objects.filter(project=project)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            # Create a task for this project
            data = request.data.copy()
            data['project'] = str(project.pk)
            serializer = TaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer

    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        return get_object_or_404(self.get_queryset(), pk=pk)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        member = self.get_object()
        if member.user != request.user:
            return Response({'error': 'Not your invitation'}, status=status.HTTP_403_FORBIDDEN)
        
        member.status = 'accepted'
        member.save()
        return Response({'message': 'Invitation accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        member = self.get_object()
        if member.user != request.user:
            return Response({'error': 'Not your invitation'}, status=status.HTTP_403_FORBIDDEN)
        
        member.status = 'rejected'
        member.save()
        return Response({'message': 'Invitation rejected'})
