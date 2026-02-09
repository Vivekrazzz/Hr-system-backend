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
