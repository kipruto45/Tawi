"""Helper to ensure a migration record exists for media_app.

This script uses Django's DB connection to check for a migration record and
will insert a record into `django_migrations` only if it is safe to do so.
Prefer running `python manage.py migrate` normally; this helper is for
exceptional cases where you need to mark a migration as applied.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
    import django
    django.setup()
except Exception:
    print('Failed to import Django; ensure virtualenv is active and you run this from the project root')
    raise

from django.db import connection
from django.utils import timezone

with connection.cursor() as cur:
    cur.execute("SELECT 1 FROM django_migrations WHERE app=%s AND name=%s", ['media_app', '0001_initial'])
    if not cur.fetchone():
        cur.execute("INSERT INTO django_migrations(app, name, applied) VALUES (%s, %s, %s)", ['media_app', '0001_initial', timezone.now()])
        connection.commit()
        print('Inserted migration record for media_app.0001')
    else:
        print('Migration record already present')

print('done')