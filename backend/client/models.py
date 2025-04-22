from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Use the API models instead of common models
from api.models import Service

User = get_user_model()


class ClientProfile(models.Model):
    """
    Extended profile information for clients
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    preferred_staff = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='preferred_by_clients')
    preferred_services = models.ManyToManyField(Service, blank=True, related_name='preferred_by_clients')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"


class ClientPreference(models.Model):
    """
    Stores client preferences for customizing their experience
    """
    client = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    reminder_time = models.IntegerField(default=24, help_text="Hours before appointment for reminder")

    def __str__(self):
        return f"{self.client.first_name}'s Preferences"