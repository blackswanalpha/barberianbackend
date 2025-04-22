from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.client'
    label = 'backend_client'  # Use a unique label to avoid potential conflicts