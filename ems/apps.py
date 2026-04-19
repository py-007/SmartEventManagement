from django.apps import AppConfig


class EmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ems'
    verbose_name = 'Event Management System'

    def ready(self):
        import ems.signals  # noqa: F401 — registers signal handlers
