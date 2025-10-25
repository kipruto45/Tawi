"""Django-aware DB inspector.

Prints tables and migration records using Django's DB connection so the
script works with Postgres or SQLite depending on the active settings.
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

print('DB vendor:', connection.vendor)
tables = connection.introspection.table_names()
print('Number of tables:', len(tables))
print('Sample tables (first 40):', tables[:40])
with connection.cursor() as cur:
    cur.execute("SELECT app, name, applied FROM django_migrations ORDER BY id LIMIT 50")
    rows = cur.fetchall()
    print('Recent migration records:')
    for r in rows:
        print(' ', r)
# Find tables that look like media_app or monitoring tables using DB-agnostic introspection
media_tables = [t for t in tables if t.startswith('media_app')]
monitoring_tables = [t for t in tables if t.startswith('monitoring')]
print('media_app tables:', media_tables)
print('monitoring tables:', monitoring_tables)

with connection.cursor() as cur:
    cur.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('media_app','monitoring') ORDER BY app, name")
    print('migration records for media_app/monitoring:')
    for r in cur.fetchall():
        print(' ', r)