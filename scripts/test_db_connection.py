import os
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    DBNAME = os.environ.get('POSTGRES_DB', 'tawi_db')
    USER = os.environ.get('POSTGRES_USER', 'postgres')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', '5432')

    if not PASSWORD:
        print('ERROR: POSTGRES_PASSWORD is not set in the environment. Set POSTGRES_PASSWORD before running this script.')
        return

    try:
        connection = psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )

        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        record = cursor.fetchone()

        print("✅ Database Connected Successfully!")
        print("PostgreSQL version:", record)

    except OperationalError as e:
        print("❌ Database connection failed!")
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_connection()
