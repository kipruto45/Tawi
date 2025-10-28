from django.apps import AppConfig
from pathlib import Path

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    path = Path(__file__).resolve().parent
    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
