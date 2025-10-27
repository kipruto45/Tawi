#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Ensure project root is on sys.path so tawi_project is importable when running
# this script from the scripts/ directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
    django.setup()
    from django.db import connection
    print('DATABASES[default]:')
    print(settings.DATABASES['default'])
    print('Connection vendor:', connection.vendor)
    try:
        with connection.cursor() as cur:
            # list tables (fast)
            t = connection.introspection.table_names()
            print('Number of tables:', len(t))
            # show otp/two_factor related tables
            otp_tables = [name for name in t if 'otp' in name or 'two_factor' in name or 'otp_' in name]
            print('OTP/two_factor-related tables:', otp_tables)
    except Exception as e:
        print('Error listing tables:', type(e).__name__, e)

if __name__ == '__main__':
    main()
