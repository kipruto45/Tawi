from django.test import Client

path = '/accounts/password_reset/'
client = Client()
resp = client.get(path)
print('GET', path, '->', resp.status_code)
try:
    body = resp.content.decode('utf-8')
except Exception:
    body = resp.content
print('\n---- RENDERED HTML START ----\n')
print(body)
print('\n---- RENDERED HTML END ----\n')
