from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.auth'
    label = 'backend_auth'  # Use a unique label to avoid conflicts with Django's built-in auth app
