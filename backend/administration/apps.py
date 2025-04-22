from django.apps import AppConfig


class AdministrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.administration'
    label = 'backend_administration'  # Unique label to avoid conflicts
