from django.apps import AppConfig


class TwofactorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'twofactor'

    def ready(self):
        import twofactor.signals
