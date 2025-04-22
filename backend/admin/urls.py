from django.urls import path
from . import views

urlpatterns = [
    # User Management
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/activate/', views.UserActivateView.as_view(), name='user-activate'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user-deactivate'),

    # Staff Management
    path('staff/', views.StaffListCreateView.as_view(), name='staff-list'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff-detail'),

    # Client Management
    path('clients/', views.ClientListCreateView.as_view(), name='client-list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),

    # Category Management
    path('categories/', views.CategoryListView.as_view(), name='admin-category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='admin-category-detail'),

    # Service Management
    path('services/', views.ServiceListView.as_view(), name='admin-service-list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='admin-service-detail'),

    # Appointment Management
    path('appointments/', views.AppointmentListView.as_view(), name='admin-appointment-list'),
    path('appointments/today/', views.TodayAppointmentsView.as_view(), name='admin-today-appointments'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='admin-appointment-detail'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='admin-appointment-cancel'),

    # Business Settings
    path('settings/', views.BusinessSettingsView.as_view(), name='admin-business-settings'),

    # Business Hours
    path('business-hours/', views.BusinessHoursListView.as_view(), name='admin-business-hours-list'),
    path('business-hours/<int:pk>/', views.BusinessHoursUpdateView.as_view(), name='admin-business-hours-update'),

    # Holiday Management
    path('holidays/', views.HolidayListView.as_view(), name='admin-holiday-list'),
    path('holidays/<int:pk>/', views.HolidayDetailView.as_view(), name='admin-holiday-detail'),

    # Reports
    path('dashboard/', views.DashboardView.as_view(), name='admin-dashboard'),
    path('reports/staff-performance/', views.StaffPerformanceReportView.as_view(), name='admin-staff-performance-report'),
    path('reports/service-analysis/', views.ServiceAnalysisReportView.as_view(), name='admin-service-analysis-report'),
    path('reports/appointment-metrics/', views.AppointmentMetricsReportView.as_view(), name='admin-appointment-metrics-report'),
    path('reports/', views.ReportListCreateView.as_view(), name='admin-report-list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='admin-report-detail'),
    path('reports/generate/', views.ReportGenerateView.as_view(), name='admin-report-generate'),

    # User Logs
    path('logs/', views.UserLogListView.as_view(), name='admin-log-list'),
    path('logs/<int:pk>/', views.UserLogDeleteView.as_view(), name='admin-log-delete'),

    # Profile Management
    path('profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    path('profile/change-password/', views.AdminChangePasswordView.as_view(), name='admin-change-password'),

    # Media Management
    path('media/', views.MediaFileListCreateView.as_view(), name='admin-media-list'),
    path('media/<int:pk>/', views.MediaFileDetailView.as_view(), name='admin-media-detail'),

    # Service Media
    path('services/<int:service_id>/media/', views.ServiceMediaCreateView.as_view(), name='admin-service-media-create'),
    path('services/media/<int:pk>/', views.ServiceMediaDeleteView.as_view(), name='admin-service-media-delete'),

    # SMS Notifications
    path('sms-notifications/', views.SMSNotificationListView.as_view(), name='admin-sms-notification-list'),
    path('sms-notifications/<int:pk>/', views.SMSNotificationDetailView.as_view(), name='admin-sms-notification-detail'),
    path('sms-notifications/send/', views.SendSMSNotificationView.as_view(), name='admin-send-sms-notification'),
    path('sms-notifications/update-status/', views.UpdateSMSStatusView.as_view(), name='admin-update-status'),
]
