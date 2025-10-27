"""Django-aware helper to remove a monitoring migration row from django_migrations."""
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

with connection.cursor() as cur:
	cur.execute("SELECT app, name FROM django_migrations WHERE app=%s AND name=%s", ['monitoring', '0002_monitoringreport'])
	print('found:', cur.fetchall())
	cur.execute("DELETE FROM django_migrations WHERE app=%s AND name=%s", ['monitoring', '0002_monitoringreport'])
	connection.commit()
	cur.execute("SELECT app, name FROM django_migrations WHERE app=%s", ['monitoring'])
	print('after:', cur.fetchall())

print('done')