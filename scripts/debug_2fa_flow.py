#!/usr/bin/env python
import os
import sys

# ensure project on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()

from django.test import Client
from django.test.utils import setup_test_environment
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.mail import get_connection
from django.test import override_settings as _override_settings_ctx
import re
from django.db import connection

print('DB vendor:', connection.vendor)
print('Tables:', len(connection.introspection.table_names()))

User = get_user_model()
username = 'debug_strict'
password = 'secret'
email = 'debug_strict@example.com'

# remove existing user if any
User.objects.filter(username=username).delete()
user = User.objects.create_user(username=username, email=email, password=password)

from django_otp.plugins.otp_email.models import EmailDevice
EmailDevice.objects.filter(user=user).delete()
EmailDevice.objects.create(user=user, name='default', confirmed=True)
# Try generating a challenge directly to see if email sending and token
# generation works outside the wizard flow.
dev = EmailDevice.objects.filter(user=user).first()
if dev:
    try:
        print('Generating challenge directly on EmailDevice...')
        dev.generate_challenge()
    except Exception as e:
        print('generate_challenge failed:', type(e).__name__, e)

ctx = _override_settings_ctx(ROOT_URLCONF='accounts.tests.tf_real_urls', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
ctx.__enter__()
setup_test_environment()
print('Test environment setup completed (mail.outbox should be present)')
from django.core import mail as mail_module
print('mail.outbox available?', hasattr(mail_module, 'outbox'))
conn_mail = get_connection()
print('conn_mail has outbox?', hasattr(conn_mail, 'outbox'))
if hasattr(conn_mail, 'outbox'):
    conn_mail.outbox.clear()
elif hasattr(mail_module, 'outbox'):
    mail_module.outbox.clear()
else:
    print('No outbox found; emails may not be captured')
client = Client()
if not hasattr(conn_mail, 'outbox'):
    # ensure locmem backend is active; warn otherwise
    print('Warning: email connection has no outbox; ensure EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend')
    conn_mail.outbox = []
conn_mail.outbox.clear()
login_url = '/account/login/'

print('GET', login_url)
get_resp = client.get(login_url)
print('status', get_resp.status_code)
# collect hidden inputs
import re
hidden_inputs = re.findall(r'<input[^>]+type="hidden"[^>]+>', get_resp.content.decode('utf-8'))
print('hidden inputs count', len(hidden_inputs))
initial_post = {}
for inp in hidden_inputs:
    name_m = re.search(r'name="([^"]+)"', inp)
    val_m = re.search(r'value="([^"]*)"', inp)
    if name_m:
        initial_post[name_m.group(1)] = val_m.group(1) if val_m else ''

initial_post.update({'auth-username': username, 'auth-password': password})
print('POST creds, keys:', list(initial_post.keys())[:10])
resp = client.post(login_url, initial_post, follow=True)
print('after creds status', resp.status_code)
print('redirect chain length', len(resp.redirect_chain))
print('Response content after credential POST:')
print(resp.content.decode('utf-8')[:1200])

print('mail outbox len', len(conn_mail.outbox))
if conn_mail.outbox:
    body = conn_mail.outbox[-1].body
    print('email body snippet:', body[:300])
    m = re.search(r"(\d{6,8})", body)
    print('token match', m)
    token = m.group(1) if m else None
else:
    token = None

# Inspect static token table to see if a token was generated
from django.db import connection as dj_conn
with dj_conn.cursor() as cur:
    try:
        cur.execute("SELECT id, token FROM otp_static_statictoken ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        print('otp_static_statictoken rows:', rows)
    except Exception as e:
        print('Failed to query otp_static_statictoken:', type(e).__name__, e)
        try:
            cur.execute("SELECT * FROM otp_email_emaildevice ORDER BY id DESC LIMIT 5")
            rows2 = cur.fetchall()
            print('otp_email_emaildevice rows (recent):', rows2)
        except Exception as e:
            print('Failed to query otp_email_emaildevice:', type(e).__name__, e)

# collect management form fields
post_data = {}
hidden_inputs_all = re.findall(r'<input[^>]+type="hidden"[^>]+>', resp.content.decode('utf-8'))
for inp in hidden_inputs_all:
    name_m = re.search(r'name="([^"]+)"', inp)
    val_m = re.search(r'value="([^"]*)"', inp)
    if name_m:
        post_data[name_m.group(1)] = val_m.group(1) if val_m else ''

post_data['token'] = token
print('Posting token, token=', token)
resp2 = client.post(login_url, post_data, follow=True)
print('after token status', resp2.status_code)
print('redirect_chain', resp2.redirect_chain)
print('user authenticated in request:', hasattr(resp2.wsgi_request, 'user') and resp2.wsgi_request.user.is_authenticated)
print('Final URL:', resp2.wsgi_request.path)

# print some response snippet
print('Response content snippet:', resp2.content.decode('utf-8')[:800])

# Exit override
try:
    ctx.__exit__(None, None, None)
except Exception:
    pass
