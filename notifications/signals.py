from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Notification
from attendance.models import LeaveRequest
from projects.models import ProjectMember
from tasks.models import Task
from django.utils import timezone

@receiver(post_save, sender=LeaveRequest)
def leave_request_notification(sender, instance, created, **kwargs):
    if created:
        if instance.manager:
            Notification.objects.create(
                recipient=instance.manager,
                sender=instance.employee,
                notification_type='leave_request',
                title='New Leave Request',
                message=f'{instance.employee.first_name} has requested {instance.leave_type} leave from {instance.start_date} to {instance.end_date}.',
                related_id=str(instance.id)
            )
    else:
        # Check if status changed
        if instance.status in ['approved', 'rejected']:
             # We might need to track old status, but for simplicity:
             Notification.objects.create(
                recipient=instance.employee,
                sender=instance.manager,
                notification_type=f'leave_{instance.status}',
                title=f'Leave {instance.status.capitalize()}',
                message=f'Your {instance.leave_type} leave request for {instance.start_date} has been {instance.status}.',
                related_id=str(instance.id)
            )

@receiver(post_save, sender=ProjectMember)
def project_invite_notification(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        Notification.objects.create(
            recipient=instance.user,
            sender=instance.invited_by,
            notification_type='project_invite',
            title='New Project Invitation',
            message=f'You have been invited to join the project "{instance.project.name}" by {instance.invited_by.first_name}.',
            related_id=str(instance.project.id)
        )

@receiver(m2m_changed, sender=Task.assigned_members.through)
def task_assigned_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from authentication.models import User
        for user_id in pk_set:
            user = User.objects.get(_id=user_id)
            Notification.objects.create(
                recipient=user,
                notification_type='task_assigned',
                title='New Task Assigned',
                message=f'You have been assigned to the task: {instance.title}.',
                related_id=str(instance.id)
            )

@receiver(post_save, sender='chat.Message')
def chat_message_notification(sender, instance, created, **kwargs):
    if created:
        recipients = []
        context = ""
        related_id = ""
        
        if instance.task:
            recipients = instance.task.assigned_members.exclude(_id=instance.sender._id)
            context = f"in task: {instance.task.title}"
            related_id = str(instance.task.id)
        elif instance.project:
            from projects.models import ProjectMember
            members = ProjectMember.objects.filter(project=instance.project, status='accepted').exclude(user=instance.sender)
            recipients = [m.user for m in members]
            context = f"in project: {instance.project.name}"
            related_id = str(instance.project.id)
            
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.sender,
                notification_type='chat_message',
                title='New Message',
                message=f'{instance.sender.first_name} sent a message {context}.',
                related_id=related_id
            )
