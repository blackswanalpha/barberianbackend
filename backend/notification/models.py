from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    """
    General notification model for in-app notifications.
    """
    TYPE_CHOICES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_completed', 'Appointment Completed'),
        ('system', 'System Notification'),
        ('marketing', 'Marketing Message'),
        ('other', 'Other'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name=_('Recipient')
    )
    title = models.CharField(_('Title'), max_length=255)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Is Read'), default=False)
    notification_type = models.CharField(
        _('Notification Type'), 
        max_length=50, 
        choices=TYPE_CHOICES,
        default='system'
    )
    reference_id = models.CharField(
        _('Reference ID'), 
        max_length=255, 
        blank=True, 
        null=True,
        help_text=_('ID of related object (e.g., appointment ID)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.title} ({self.recipient.email})"

class NotificationPreference(models.Model):
    """
    User preferences for different types of notifications.
    """
    TYPE_CHOICES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_completed', 'Appointment Completed'),
        ('system', 'System Notification'),
        ('marketing', 'Marketing Message'),
    )
    
    CHANNEL_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences',
        verbose_name=_('User')
    )
    notification_type = models.CharField(
        _('Notification Type'), 
        max_length=50, 
        choices=TYPE_CHOICES
    )
    channel = models.CharField(
        _('Channel'), 
        max_length=20, 
        choices=CHANNEL_CHOICES
    )
    is_enabled = models.BooleanField(_('Is Enabled'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
        unique_together = ['user', 'notification_type', 'channel']
    
    def __str__(self):
        return f"{self.user.email} - {self.notification_type} via {self.channel} ({'Enabled' if self.is_enabled else 'Disabled'})"

class SMSNotification(models.Model):
    """
    Model to track SMS notifications sent via Twilio.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('undelivered', 'Undelivered'),
        ('received', 'Received'),
        ('read', 'Read'),
    )
    
    TYPE_CHOICES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('manual', 'Manual Message'),
        ('marketing', 'Marketing Message'),
        ('other', 'Other'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='sms_notifications',
        verbose_name=_('Recipient'),
        null=True,
        blank=True,
        help_text=_('User associated with this SMS (optional)')
    )
    phone_number = models.CharField(_('Phone Number'), max_length=20)
    message = models.TextField(_('Message'))
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    twilio_sid = models.CharField(
        _('Twilio SID'), 
        max_length=255, 
        blank=True, 
        null=True,
        help_text=_('Twilio message SID for tracking')
    )
    notification_type = models.CharField(
        _('Notification Type'), 
        max_length=50, 
        choices=TYPE_CHOICES,
        default='other'
    )
    reference_id = models.CharField(
        _('Reference ID'), 
        max_length=255, 
        blank=True, 
        null=True,
        help_text=_('ID of related object (e.g., appointment ID)')
    )
    error_message = models.TextField(
        _('Error Message'), 
        blank=True, 
        null=True,
        help_text=_('Error details if the SMS failed')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('SMS Notification')
        verbose_name_plural = _('SMS Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} to {self.phone_number} ({self.status})"