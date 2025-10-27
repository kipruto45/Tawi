#!/usr/bin/env python
"""Create the PostgreSQL test database used by Django's test runner.

This script connects to the server (using POSTGRES_HOST/PORT/USER/PASSWORD) and
creates a database named `test_tawi_db` if it doesn't exist. Use it when you
want to pre-create and migrate a test DB so Django's test runner can reuse it
with --keepdb and avoid test DB creation/sync issues.
"""
import os
import sys

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except Exception as e:
    print('psycopg2 is required to run this helper. Install with: pip install psycopg2-binary')
    raise

DB_NAME = os.environ.get('POSTGRES_DB', 'tawi_db')
TEST_DB = os.environ.get('TEST_DB', f'test_{DB_NAME}')
HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
PORT = int(os.environ.get('POSTGRES_PORT', '5432'))
USER = os.environ.get('POSTGRES_USER', 'postgres')
PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')

if not PASSWORD:
    print('ERROR: POSTGRES_PASSWORD not set in the environment. Set POSTGRES_PASSWORD before running this helper (or pass it in your environment/CI secrets).')
    sys.exit(2)

def main():
    print(f'Connecting to Postgres at {HOST}:{PORT} as {USER} to ensure database {TEST_DB} exists...')
    conn = psycopg2.connect(dbname='postgres', user=USER, password=PASSWORD, host=HOST, port=PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (TEST_DB,))
    if cur.fetchone():
        print('Test DB already exists:', TEST_DB)
    else:
        print('Creating database', TEST_DB)
        cur.execute('CREATE DATABASE %s' % (psycopg2.extensions.AsIs(TEST_DB),))
        print('Created')
    cur.close()
    conn.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Failed to create test DB:', type(e).__name__, e)
        sys.exit(1)
    print('Done')
