from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.test import Client

User = get_user_model()
email = 'notif-test@example.com'
user, created = User.objects.get_or_create(email=email, defaults={'username': 'notiftest'})
if created:
    user.set_password('password123')
    user.save()

# create some notifications
Notification.objects.create(recipient=user, verb='Welcome', description='Welcome to Tawi')
Notification.objects.create(recipient=user, verb='Report Ready', description='Your report is ready')

client = Client()
logged_in = client.login(username=user.username, password='password123')
print('Logged in:', logged_in)
resp = client.get('/notifications/page/')
print('GET /notifications/page/ ->', resp.status_code)
body = resp.content.decode('utf-8')
start = body.find('<div class="card')
snippet = body[start:start+1000] if start!=-1 else body[:1000]
print('\nRendered snippet:\n')
print(snippet)
