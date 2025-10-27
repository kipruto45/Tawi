import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tawi_project.settings'
os.environ['USE_2FA'] = '1'
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.locmem.EmailBackend'

import django
import sys
sys.path.insert(0, os.getcwd())
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core import mail
import re

User = get_user_model()
import uuid
username = f'inspect_{uuid.uuid4().hex[:8]}'
password = 'pw'
email = f'{username}@example.com'
user = User.objects.create_user(username=username, email=email, password=password)
from django_otp.plugins.otp_email.models import EmailDevice
EmailDevice.objects.create(user=user, name='default', confirmed=True)

c = Client()
# clear outbox
try:
    mail.outbox.clear()
except Exception:
    conn = mail.get_connection()
    if hasattr(conn, 'outbox'):
        conn.outbox.clear()

# first GET login to collect hidden inputs
get_resp = c.get('/account/login/')
print('GET status:', get_resp.status_code)
hidden = re.findall(r'<input[^>]+type=\"hidden\"[^>]+>', get_resp.content.decode('utf-8'))
print('Hidden on GET:', len(hidden))
initial_post = {}
for inp in hidden:
    name_m = re.search(r'name=\"([^\"]+)\"', inp)
    val_m = re.search(r'value=\"([^\"]*)\"', inp)
    if name_m:
        initial_post[name_m.group(1)] = val_m.group(1) if val_m else ''

initial_post.update({'username': username, 'password': password})
print('Posting login with hidden fields...')
resp = c.post('/account/login/', initial_post, follow=True)
print('Status:', resp.status_code)
content = resp.content.decode('utf-8')
# print first 4000 chars to avoid flooding
print('Response length', len(content))

hidden = re.findall(r'<input[^>]+type="hidden"[^>]+>', content)
print('Found hidden inputs:', len(hidden))
for inp in hidden:
    name_m = re.search(r'name="([^"]+)"', inp)
    val_m = re.search(r'value="([^"]*)"', inp)
    print('  ', name_m.group(1) if name_m else None, '=>', val_m.group(1) if val_m else '')

print('\nOutbox size:', len(getattr(mail, 'outbox', getattr(mail.get_connection(), 'outbox', []))))
if getattr(mail, 'outbox', None):
    print('\nEmail body:')
    print(mail.outbox[-1].body)
else:
    conn = mail.get_connection()
    if hasattr(conn, 'outbox') and conn.outbox:
        print('\nEmail body:')
        print(conn.outbox[-1].body)

print('\nFull response (truncated):\n')
print(content[:4000])
