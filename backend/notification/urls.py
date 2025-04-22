from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    # Regular notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/delete/', views.DeleteNotificationView.as_view(), name='notification-delete'),
    path('delete-all/', views.DeleteAllNotificationsView.as_view(), name='notification-delete-all'),
    
    # SMS Notifications (admin only)
    path('sms/', views.SMSNotificationListView.as_view(), name='sms-list'),
    path('sms/<int:pk>/', views.SMSNotificationDetailView.as_view(), name='sms-detail'),
    path('sms/send/', views.SendSMSManualView.as_view(), name='sms-send'),
    path('sms/update-status/', views.UpdateSMSStatusView.as_view(), name='sms-update-status'),
]