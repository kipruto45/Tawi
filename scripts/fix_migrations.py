"""Django-aware helper to remove specific migration history rows.

This script uses Django's DB connection to inspect and modify rows in
`django_migrations`. It is safe to run against the active DB (Postgres or
SQLite) as long as you understand it will permanently remove migration
history rows. Use for fixing out-of-order migration history entries.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
	import django
	django.setup()
except Exception as e:
	print('Failed to import Django; ensure this script is run from the project root and the virtualenv is activated.')
	raise

from django.db import connection

def main():
	with connection.cursor() as cur:
		cur.execute("SELECT app, name, applied FROM django_migrations WHERE app=%s", ['monitoring'])
		before = cur.fetchall()
		print('before:', before)

		cur.execute("DELETE FROM django_migrations WHERE app=%s AND name=%s", ['monitoring', '0002_monitoringreport'])
		connection.commit()

		cur.execute("SELECT app, name, applied FROM django_migrations WHERE app=%s", ['monitoring'])
		after = cur.fetchall()
		print('after:', after)

	print('done')

if __name__ == '__main__':
	main()