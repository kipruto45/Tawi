import sqlite3
from pathlib import Path
import datetime
DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'
print('Using DB:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
now = datetime.datetime.utcnow().isoformat()
for name in ('0002_auto_add_fields','0003_alter_treeupdate_options_alter_tree_qr_image'):
    cur.execute("SELECT 1 FROM django_migrations WHERE app=? AND name=?", ('trees', name))
    if not cur.fetchone():
        cur.execute("INSERT INTO django_migrations(app, name, applied) VALUES(?,?,?)", ('trees', name, now))
        print('Inserted', name)
    else:
        print('Already present', name)
conn.commit()
cur.execute("SELECT app, name FROM django_migrations WHERE app='trees'")
print('trees now:', cur.fetchall())
conn.close()
print('done')
