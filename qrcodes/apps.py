from django.apps import AppConfig
from pathlib import Path

class QrcodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qrcodes'
    path = Path(__file__).resolve().parent
