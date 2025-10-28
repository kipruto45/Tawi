from django.apps import AppConfig
from pathlib import Path

class MediaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_app'
    path = Path(__file__).resolve().parent
    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
