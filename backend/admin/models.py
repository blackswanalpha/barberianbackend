from django.db import models
from django.conf import settings
import json

class UserLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"

class Report(models.Model):
    REPORT_TYPES = (
        ('staff_performance', 'Staff Performance'),
        ('service_analysis', 'Service Analysis'),
        ('appointment_metrics', 'Appointment Metrics'),
        ('revenue', 'Revenue Report'),
        ('client_activity', 'Client Activity'),
        ('custom', 'Custom Report'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    parameters = models.JSONField(default=dict)  # Store report parameters as JSON
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.report_type})"

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, params_dict):
        self.parameters = params_dict
        self.save()

class MediaFile(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='media_files/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_media')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=255, blank=True)  # Comma-separated tags

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
