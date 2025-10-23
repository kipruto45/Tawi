import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'db.sqlite3'

def main():
    if not DB.exists():
        print('No sqlite db found at', DB)
        return 1

    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    cur.execute("SELECT app, name FROM django_migrations ORDER BY id")
    rows = cur.fetchall()
    apps = {}
    for app, name in rows:
        apps.setdefault(app, []).append(name)

    print('Migration counts:')
    for app, names in apps.items():
        print(f'  {app}: {len(names)}')

    # If admin has migrations and accounts has none, remove admin rows to allow correct ordering
    if 'admin' in apps and 'accounts' not in apps:
        print('\nDetected admin migrations applied before accounts. Removing admin entries from django_migrations...')
        cur.execute("DELETE FROM django_migrations WHERE app = 'admin'")
        conn.commit()
        print('Deleted admin migration rows. You can now run manage.py migrate to apply migrations in order.')
        return 0

    print('\nNo inconsistent history detected by this script. Nothing changed.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
