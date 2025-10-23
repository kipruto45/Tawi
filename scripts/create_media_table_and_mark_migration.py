import sqlite3
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
# Create media table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS media_app_media (
    id integer PRIMARY KEY AUTOINCREMENT,
    file varchar(100) NOT NULL,
    file_type varchar(16) NOT NULL,
    uploaded_at datetime NOT NULL,
    title varchar(255),
    description text,
    thumbnail varchar(100),
    latitude real,
    longitude real,
    taken_at datetime,
    site_id integer,
    tree_id integer,
    uploader_id integer
);
""")
# Insert migration record if missing
cur.execute("SELECT 1 FROM django_migrations WHERE app='media_app' AND name='0001_initial'")
if not cur.fetchone():
    import datetime
    cur.execute("INSERT INTO django_migrations(app,name,applied) VALUES (?,?,?)",
                ('media_app','0001_initial', datetime.datetime.now().isoformat()))
    print('Inserted migration record for media_app.0001')
else:
    print('Migration record already present')
conn.commit()
conn.close()
print('done')