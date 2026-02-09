from django.contrib import admin
from .models import Project, ProjectMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'created_by', 'created_at')
    search_fields = ('name', 'company_name')

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'status', 'role', 'joined_at')
    list_filter = ('status', 'role')
