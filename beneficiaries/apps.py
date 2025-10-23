from django.apps import AppConfig
from pathlib import Path

class BeneficiariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beneficiaries'
    path = Path(__file__).resolve().parent
