import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'
print('Using DB:', DB)
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT app, name FROM django_migrations WHERE app='trees'")
print('Before:', cur.fetchall())
# Remove problematic migrations that are recorded as applied out-of-order
for name in ('0003_alter_treeupdate_options_alter_tree_qr_image', '0002_auto_add_fields'):
	cur.execute("DELETE FROM django_migrations WHERE app=? AND name=?", ('trees', name))
conn.commit()
cur.execute("SELECT app, name FROM django_migrations WHERE app='trees'")
print('After:', cur.fetchall())
conn.close()
print('done')