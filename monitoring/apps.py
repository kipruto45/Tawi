from django.apps import AppConfig
from pathlib import Path

class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    path = Path(__file__).resolve().parent
