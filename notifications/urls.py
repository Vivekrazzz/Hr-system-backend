from django.urls import path
from .views import NotificationListView, unread_count, mark_as_read, mark_all_as_read

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread_count/', unread_count, name='unread-count'),
    path('<str:pk>/mark_as_read/', mark_as_read, name='mark-as-read'),
    path('mark_all_as_read/', mark_all_as_read, name='mark-all-as-read'),
]
