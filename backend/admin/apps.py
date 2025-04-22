from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.admin'
    label = 'backend_admin'  # Use a unique label to avoid conflicts with Django's built-in admin app
