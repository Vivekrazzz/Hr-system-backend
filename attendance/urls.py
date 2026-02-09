from django.urls import path
from .views import CheckInView, CheckOutView, AttendanceListView, AttendanceStatusView

urlpatterns = [
    path('logs/', AttendanceListView.as_view(), name='attendance-logs'),
    path('checkin/', CheckInView.as_view(), name='checkin'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('status/', AttendanceStatusView.as_view(), name='attendance-status'),
]
