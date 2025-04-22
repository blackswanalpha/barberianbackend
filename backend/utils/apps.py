from django.apps import AppConfig


class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.utils'
    label = 'backend_utils'  # Use a unique label to avoid conflicts