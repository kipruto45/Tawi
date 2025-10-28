from django.apps import AppConfig
from pathlib import Path

class TreesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trees'
    path = Path(__file__).resolve().parent

    def ready(self):
        # import signal handlers to ensure QRCode creation on Tree save
        try:
            import trees.signals  # noqa: F401
        except Exception:
            pass
