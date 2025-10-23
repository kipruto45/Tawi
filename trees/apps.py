from django.apps import AppConfig
from pathlib import Path

class TreesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trees'
    path = Path(__file__).resolve().parent
