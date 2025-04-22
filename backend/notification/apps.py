from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.notification'
    label = 'backend_notification'

    def ready(self):
        import backend.notification.signals