import sqlite3, datetime
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
cur.execute("SELECT 1 FROM django_migrations WHERE app='monitoring' AND name='0002_monitoringreport'")
if not cur.fetchone():
    cur.execute("INSERT INTO django_migrations(app,name,applied) VALUES (?,?,?)",
                ('monitoring','0002_monitoringreport', datetime.datetime.now().isoformat()))
    conn.commit()
    print('Inserted monitoring.0002')
else:
    print('monitoring.0002 already present')
conn.close()