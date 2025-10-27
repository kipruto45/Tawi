import os
import sys
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
    import django
    django.setup()
except Exception:
    print('Failed to import Django; run this from the project root with the virtualenv active')
    raise

from django.db import connection

with connection.cursor() as cur:
    cur.execute("SELECT 1 FROM django_migrations WHERE app='monitoring' AND name='0002_monitoringreport'")
    if not cur.fetchone():
        cur.execute("INSERT INTO django_migrations(app,name,applied) VALUES (?,?,?)",
                    ('monitoring','0002_monitoringreport', datetime.datetime.now().isoformat()))
        # commit the write
        connection.commit()
        print('Inserted monitoring.0002')
    else:
        print('monitoring.0002 already present')