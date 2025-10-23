import os
import sys
import django

# ensure project root is on sys.path so settings module can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser: admin')
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

client = Client()
logged = client.login(username='admin', password='adminpass')
print('logged in:', logged)
resp = client.get('/dashboard/api/summary/')
print('status_code:', resp.status_code)
try:
    print('response JSON keys:', list(resp.json().keys()))
    print('data keys:', list(resp.json().get('data', {}).keys()))
except Exception as e:
    print('response content:', resp.content)
    print('error parsing JSON:', e)
