from django.db import models
from django.conf import settings

class StaffSettings(models.Model):
    """
    Settings and preferences for staff members
    """
    NOTIFICATION_PREFERENCES = (
        ('all', 'All Notifications'),
        ('appointments_only', 'Appointments Only'),
        ('important_only', 'Important Only'),
        ('none', 'None'),
    )
    
    staff = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_settings')
    notification_preference = models.CharField(max_length=20, choices=NOTIFICATION_PREFERENCES, default='all')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    auto_confirm_appointments = models.BooleanField(default=False)
    calendar_view_preference = models.CharField(max_length=10, choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month')], default='week')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Staff Settings'
        verbose_name_plural = 'Staff Settings'
    
    def __str__(self):
        return f"{self.staff.get_full_name()}'s Settings"
