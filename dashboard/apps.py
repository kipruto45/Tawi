from django.apps import AppConfig
from pathlib import Path

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    path = Path(__file__).resolve().parent

    def ready(self):
        # import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
