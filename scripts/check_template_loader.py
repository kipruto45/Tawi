"""
Check that the canonical logo static file exists using Django's staticfiles finders.

This avoids loading any template include and simply verifies the file path.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
    import django
    django.setup()
    from django.contrib.staticfiles import finders
except Exception as e:
    print('DJANGO SETUP ERROR:', repr(e))
    sys.exit(2)

logo_path = finders.find('img/tawi_logo.png')
if logo_path:
    print('FOUND logo static file at:', logo_path)
else:
    print("Logo static file 'img/tawi_logo.png' not found via staticfiles finders")
