import sqlite3, os
DB='D:/Tree_planting/db.sqlite3'
print('db exists', os.path.exists(DB))
if not os.path.exists(DB):
    raise SystemExit('db missing')
conn=sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'media_app%';")
print('media_app tables:', cur.fetchall())
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'monitoring%';")
print('monitoring tables:', cur.fetchall())
cur.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('media_app','monitoring') ORDER BY app, name")
print('migration records:')
for r in cur.fetchall():
    print(r)
conn.close()