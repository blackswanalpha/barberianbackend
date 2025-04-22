from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.StaffLoginView.as_view(), name='staff-login'),

    # Schedule Management
    path('schedules/', views.StaffScheduleListView.as_view(), name='staff-schedule-list'),
    path('schedules/create/', views.StaffScheduleCreateView.as_view(), name='staff-schedule-create'),
    path('schedules/<int:pk>/', views.StaffScheduleDetailView.as_view(), name='staff-schedule-detail'),
    path('schedules/<int:pk>/update/', views.StaffScheduleUpdateView.as_view(), name='staff-schedule-update'),
    path('schedules/<int:pk>/delete/', views.StaffScheduleDeleteView.as_view(), name='staff-schedule-delete'),

    # Appointment Management
    path('appointments/', views.StaffAppointmentListView.as_view(), name='staff-appointment-list'),
    path('appointments/today/', views.StaffTodayAppointmentsView.as_view(), name='staff-today-appointments'),
    path('appointments/upcoming/', views.StaffUpcomingAppointmentsView.as_view(), name='staff-upcoming-appointments'),
    path('appointments/<int:pk>/', views.StaffAppointmentDetailView.as_view(), name='staff-appointment-detail'),
    path('appointments/<int:pk>/status/', views.AppointmentStatusUpdateView.as_view(), name='staff-appointment-status-update'),

    # Service Browsing
    path('services/', views.StaffServicesView.as_view(), name='staff-services'),

    # Profile Management
    path('profile/', views.StaffProfileView.as_view(), name='staff-profile'),
    path('profile/update/', views.StaffProfileUpdateView.as_view(), name='staff-profile-update'),
    path('profile/change-password/', views.StaffChangePasswordView.as_view(), name='staff-change-password'),

    # Settings Management
    path('settings/', views.StaffSettingsUpdateView.as_view(), name='staff-settings'),
    path('availability/', views.StaffAvailabilityToggleView.as_view(), name='staff-availability-toggle'),

    # Notification Management
    path('notifications/', views.StaffNotificationListView.as_view(), name='staff-notification-list'),
]
