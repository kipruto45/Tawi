"""
Utility: create a dev superuser non-interactively if no superusers exist.
Run: .\.venv\Scripts\python.exe scripts/create_dev_superuser.py
"""
import os
import sys
import django

# Ensure project root is on sys.path so tawi_project is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    print('Creating dev superuser: admin')
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    print('Superuser created: username=admin password=adminpass')
else:
    print('Superuser already exists')
