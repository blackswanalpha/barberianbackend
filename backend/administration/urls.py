from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('users/', views.user_management_view, name='user_management'),
    path('staff/', views.staff_management_view, name='staff_management'),
    path('settings/', views.system_settings_view, name='system_settings'),
]
