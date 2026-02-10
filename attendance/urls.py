from django.urls import path
from .views import (
    CheckInView, CheckOutView, AttendanceListView, AttendanceStatusView,
    LeaveRequestCreateView, MyLeaveRequestListView, SubordinateLeaveRequestListView,
    LeaveApprovalView, WhosOnLeaveView
)

urlpatterns = [
    path('logs/', AttendanceListView.as_view(), name='attendance-logs'),
    path('checkin/', CheckInView.as_view(), name='checkin'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('status/', AttendanceStatusView.as_view(), name='attendance-status'),
    
    # Leave Management
    path('leaves/request/', LeaveRequestCreateView.as_view(), name='leave-request'),
    path('leaves/my/', MyLeaveRequestListView.as_view(), name='my-leaves'),
    path('leaves/subordinate/', SubordinateLeaveRequestListView.as_view(), name='subordinate-leaves'),
    path('leaves/approve/<str:id>/', LeaveApprovalView.as_view(), name='approve-leave'),
    path('leaves/whos-out/', WhosOnLeaveView.as_view(), name='whos-out'),
]
