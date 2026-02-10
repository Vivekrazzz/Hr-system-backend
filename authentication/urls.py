from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserDetailView, EmployeeListView, AdminCreateEmployeeView, AdminUserDetailView, ResetPasswordView, MyTokenObtainPairView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/<str:pk>/', AdminUserDetailView.as_view(), name='manage_employee'),
    path('employees/<str:pk>/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('admin/register/', AdminCreateEmployeeView.as_view(), name='admin_register_employee'),
]
