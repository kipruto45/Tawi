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

now = datetime.datetime.utcnow().isoformat()
names = ('0002_auto_add_fields','0003_alter_treeupdate_options_alter_tree_qr_image')
with connection.cursor() as cur:
    for name in names:
        cur.execute("SELECT 1 FROM django_migrations WHERE app=%s AND name=%s", ('trees', name))
        if not cur.fetchone():
            cur.execute("INSERT INTO django_migrations(app, name, applied) VALUES(%s,%s,%s)", ('trees', name, now))
            print('Inserted', name)
        else:
            print('Already present', name)
    connection.commit()
    cur.execute("SELECT app, name FROM django_migrations WHERE app='trees'")
    print('trees now:', cur.fetchall())

print('done')
