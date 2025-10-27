import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tawi_project.settings'
os.environ['USE_2FA'] = '1'
# use locmem email backend so we can inspect mail.outbox here
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.locmem.EmailBackend'
import django
import sys
sys.path.insert(0, os.getcwd())
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()
# avoid touching existing users (cascade can reference tables that aren't present here).
import uuid
dbg_username = f"dbguser_{uuid.uuid4().hex[:8]}"
user = User.objects.create_user(username=dbg_username, email=f"{dbg_username}@example.com", password='pw')
print('CREATED USER', dbg_username)
from django_otp.plugins.otp_email.models import EmailDevice
ed = EmailDevice.objects.create(user=user, name='default', confirmed=True)
print('CREATED EMAILDEVICE id=', getattr(ed, 'id', None))

c = Client()
print('CREATED TEST CLIENT')
# ensure we can inspect sent mail; try mail.outbox or the backend connection outbox
def _get_outbox():
    try:
        if hasattr(mail, 'outbox'):
            return mail.outbox
    except Exception:
        pass
    try:
        conn = mail.get_connection()
        return getattr(conn, 'outbox', [])
    except Exception:
        return []

outbox = _get_outbox()
if hasattr(outbox, 'clear'):
    outbox.clear()
print('CLEARED OUTBOX')
print('ABOUT TO POST LOGIN')
import traceback
try:
    resp = c.post('/account/login/', {'username': dbg_username, 'password': 'pw'}, follow=True)
    print('STATUS', resp.status_code)
    print('REDIRECTS', resp.redirect_chain)
    print('LENGTH', len(resp.content))
    print('CONTEXT KEYS', list(resp.context.keys()) if resp.context else None)
except Exception as e:
    print('EXCEPTION DURING CLIENT POST:')
    traceback.print_exc()
    raise
if resp.context and 'wizard' in resp.context:
    mgmt = resp.context['wizard'].management_form
    print('MGMT FIELDS:', list(mgmt.fields.keys()))
    for name in mgmt.fields:
        try:
            print('FIELD', name, 'value', mgmt[name].value())
        except Exception as e:
            print('FIELD', name, 'value exception', e)

print('\nMAIL OUTBOX\n')
for m in mail.outbox:
    print('SUBJ', m.subject)
    print(m.body)

print('\nRESPONSE HTML\n')
print(resp.content.decode('utf-8'))
