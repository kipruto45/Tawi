#!/usr/bin/env python
"""Drop the Django test database specified by DJANGO_TEST_DB_NAME or default.

This helper terminates connections to the test DB and drops it. Use it
before a fresh `manage.py test` run when you want test DB creation to be
performed from scratch.
"""
import os
import sys
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from psycopg2 import sql
except Exception:
    print('psycopg2 is required. Install with: pip install psycopg2-binary')
    raise

DB = os.environ.get('DJANGO_TEST_DB_NAME') or os.environ.get('POSTGRES_TEST_DB') or f"test_{os.environ.get('POSTGRES_DB','tawi_db')}"
USER = os.environ.get('POSTGRES_USER', 'postgres')
PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
PORT = os.environ.get('POSTGRES_PORT', '5432')

if not PASSWORD:
    print('ERROR: POSTGRES_PASSWORD not set in environment; cannot drop test DB safely.')
    sys.exit(2)

print(f"Connecting to Postgres at {HOST}:{PORT} as {USER} to drop DB {DB} if present...")
conn = psycopg2.connect(dbname='postgres', user=USER, password=PASSWORD, host=HOST, port=PORT)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
try:
    # Terminate connections to the DB
    cur.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s"), (DB,))
    cur.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(DB)))
    print('Dropped test DB (if it existed):', DB)
except Exception as e:
    print('Failed to drop test DB:', type(e).__name__, e)
    sys.exit(1)
finally:
    cur.close()
    conn.close()
