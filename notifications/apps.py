from django.apps import AppConfig
from pathlib import Path

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    path = Path(__file__).resolve().parent
