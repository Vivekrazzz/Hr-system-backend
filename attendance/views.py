from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer

class CheckInView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        
        # Get or create daily document manually to be more robust with Djongo
        attendance = Attendance.objects.filter(employee_id=user.pk, date=today).first()
        if not attendance:
            # print(f"Creating new record for {user.email} on {today}")
            attendance = Attendance.objects.create(
                employee=user, 
                date=today,
                entries=[],
                total_hours=0
            )
        
        # Check for active entry (prevent double check-in)
        if any(e.get('check_out') is None for e in attendance.entries):
             return Response({"error": "Already checked in. Please check out first."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new entry
        new_entry = {
            'check_in': now,
            'check_out': None,
            'lat_in': request.data.get('check_in_lat') or 0.0,
            'lng_in': request.data.get('check_in_lng') or 0.0,
            'lat_out': 0.0,
            'lng_out': 0.0,
            'location_in': request.data.get('location_in', 'Kathmandu'), 
            'location_out': '',
            'note_in': request.data.get('check_in_note', ''),
            'note_out': '',
        }
        
        entries = list(attendance.entries)
        entries.append(new_entry)
        attendance.entries = entries
        attendance.save()
        
        return Response({"message": "Checked in successfully"}, status=status.HTTP_201_CREATED)

class CheckOutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        
        attendance = Attendance.objects.filter(employee_id=user.pk, date=today).first()
        if not attendance:
            return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find active entry
        active_entry = next((e for e in attendance.entries if e.get('check_out') is None), None)
        if not active_entry:
            return Response({"error": "No active check-in found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update entry
        active_entry['check_out'] = now
        active_entry['lat_out'] = request.data.get('check_out_lat')
        active_entry['lng_out'] = request.data.get('check_out_lng')
        active_entry['location_out'] = request.data.get('location_out', 'Kathmandu')
        active_entry['note_out'] = request.data.get('check_out_note')
        
        # Force Djongo to detect change by creating a new list of dicts
        attendance.entries = [e.copy() for e in attendance.entries]
        attendance.calculate_total_hours()
        attendance.save()
        
        return Response({"message": "Checked out successfully", "total_hours": attendance.total_hours})

class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        date_str = self.request.query_params.get('date')
        
        # Determine the date to filter by
        filter_date = timezone.now().date()
        if date_str:
            try:
                # Expected format: YYYY-MM-DD
                from datetime import datetime
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                 pass

        queryset = Attendance.objects.filter(date=filter_date)

        # Apply role-based filtering
        if hasattr(user, 'role') and user.role == 'employee':
            queryset = queryset.filter(employee_id=user.pk)
            
        return queryset.order_by('-date') 

class AttendanceStatusView(generics.RetrieveAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        attendance = Attendance.objects.filter(employee_id=request.user.pk, date=today).first()
        
        is_checked_in = False
        if attendance:
            is_checked_in = any(e.get('check_out') is None for e in attendance.entries)
            
        return Response({
            "is_checked_in": is_checked_in, 
            "attendance": AttendanceSerializer(attendance).data if attendance else None
        })

# Leave Management Views
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer

class LeaveRequestView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user).order_by('-applied_on')

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

class SubordinateLeaveListView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return LeaveRequest.objects.all().order_by('-applied_on')
        # If manager, show only their subordinates' leaves
        # This assumes User model has a manager field as seen in earlier turns
        return LeaveRequest.objects.filter(employee__manager=user).order_by('-applied_on')

class LeaveApprovalView(generics.UpdateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        from bson import ObjectId
        from django.shortcuts import get_object_or_404
        pk = self.kwargs.get('pk')
        if pk and isinstance(pk, str) and len(pk) == 24:
            try: pk = ObjectId(pk)
            except: pass
        return get_object_or_404(LeaveRequest, pk=pk)

    def patch(self, request, *args, **kwargs):
        leave_request = self.get_object()
        user = request.user
        
        # Check permissions: only manager or admin can approve
        if user.role != 'admin' and leave_request.employee.manager != user:
            return Response({"error": "Not authorized to process this leave request"}, status=status.HTTP_403_FORBIDDEN)
            
        status_val = request.data.get('status')
        if status_val not in ['approved', 'rejected']:
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
            
        leave_request.status = status_val
        leave_request.processed_by = user
        leave_request.process_note = request.data.get('note', '')
        leave_request.save()
        
        return Response(LeaveRequestSerializer(leave_request).data)

class WhosOutView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        today = timezone.now().date()
        return LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        )
