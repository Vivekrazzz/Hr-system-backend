"""
Main URL Configuration for HR System

This file routes all incoming requests to the appropriate app endpoints.
It includes API routes for authentication, tasks, attendance, projects, chat, and notifications.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


# ============================================================================
# HOME VIEW
# ============================================================================

def home(request):
    """
    Simple home view to verify the backend is running.
    Returns a basic HTML response.
    """
    return HttpResponse("<h1>HR System Backend is running</h1>")


# ============================================================================
# URL PATTERNS
# ============================================================================

urlpatterns = [
    # Home page
    path('', home, name='home'),
    
    # Django admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('authentication.urls')),      # User authentication & registration
    path('api/tasks/', include('tasks.urls')),              # Task management
    path('api/attendance/', include('attendance.urls')),    # Attendance tracking
    path('api/projects/', include('projects.urls')),        # Project & team management
    path('api/chat/', include('chat.urls')),                # Team communication
    path('api/notifications/', include('notifications.urls')),  # Notifications
]


# ============================================================================
# MEDIA FILES (Development only)
# ============================================================================

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
