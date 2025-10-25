import os
import sys
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
    import django
    django.setup()
except Exception:
    print('Failed to import Django; ensure virtualenv is activated and you run this from project root')
    raise

from django.db import connection

def main():
    with connection.cursor() as cur:
        cur.execute("SELECT app, name FROM django_migrations ORDER BY id")
        rows = cur.fetchall()
        apps = {}
        for app, name in rows:
            apps.setdefault(app, []).append(name)

        print('Migration counts:')
        for app, names in apps.items():
            print(f'  {app}: {len(names)}')

        if 'admin' in apps and 'accounts' not in apps:
            print('\nDetected admin migrations applied before accounts. Removing admin entries from django_migrations...')
            cur.execute("DELETE FROM django_migrations WHERE app = %s", ['admin'])
            connection.commit()
            print('Deleted admin migration rows. You can now run manage.py migrate to apply migrations in order.')
            return 0

        print('\nNo inconsistent history detected by this script. Nothing changed.')
        return 0

if __name__ == '__main__':
    sys.exit(main())
