from django.apps import AppConfig


class AIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'
    verbose_name = 'AI Integration'

    def ready(self):
        # Import signals if needed
        pass
