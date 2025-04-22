from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, RegisterView,
    UserProfileView, ChangePasswordView, LogoutView
)
from barberian.admin.views import AdminLoginView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
]
