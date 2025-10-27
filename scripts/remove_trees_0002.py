"""Django-aware helper to remove specific tree migrations from django_migrations."""
import os
import sys
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
	import django
	django.setup()
except Exception:
	print('Failed to import Django; ensure virtualenv is active and you run this from the project root')
	raise

from django.db import connection

print('Using project DB via Django settings')
with connection.cursor() as cur:
	cur.execute("SELECT app, name FROM django_migrations WHERE app=%s", ['trees'])
	print('Before:', cur.fetchall())
	# Remove problematic migrations that are recorded as applied out-of-order
	for name in ('0003_alter_treeupdate_options_alter_tree_qr_image', '0002_auto_add_fields'):
		cur.execute("DELETE FROM django_migrations WHERE app=%s AND name=%s", ['trees', name])
	connection.commit()
	cur.execute("SELECT app, name FROM django_migrations WHERE app=%s", ['trees'])
	print('After:', cur.fetchall())

print('done')