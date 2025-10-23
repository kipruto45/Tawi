from django.apps import AppConfig
from pathlib import Path

class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedback'
    path = Path(__file__).resolve().parent
