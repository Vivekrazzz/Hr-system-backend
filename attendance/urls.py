from django.urls import path
from .views import (
    CheckInView, CheckOutView, AttendanceListView, AttendanceStatusView,
    LeaveRequestView, SubordinateLeaveListView, LeaveApprovalView, WhosOutView
)

urlpatterns = [
    path('logs/', AttendanceListView.as_view(), name='attendance-logs'),
    path('checkin/', CheckInView.as_view(), name='checkin'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('status/', AttendanceStatusView.as_view(), name='attendance-status'),
    
    # Leave Management
    path('leaves/request/', LeaveRequestView.as_view(), name='leave-request'),
    path('leaves/my/', LeaveRequestView.as_view(), name='leave-list-my'),
    path('leaves/subordinate/', SubordinateLeaveListView.as_view(), name='leave-list-subordinate'),
    path('leaves/approve/<str:pk>/', LeaveApprovalView.as_view(), name='leave-approve'),
    path('leaves/whos-out/', WhosOutView.as_view(), name='leave-whos-out'),
]
