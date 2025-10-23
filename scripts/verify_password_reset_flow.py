from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import re

email = 'tawiproject@gmail.com'
User = get_user_model()
user, created = User.objects.get_or_create(email=email, defaults={'username': email})
if created:
    user.set_unusable_password()
    user.is_active = True
    user.save()
    print(f'Created user {email}')
else:
    print(f'User {email} already exists')

client = Client()
path = '/accounts/password_reset/'
resp = client.post(path, {'email': email}, follow=True)
print('POST', path, '->', resp.status_code)
print('Redirect chain:', resp.redirect_chain)

# Compute the uid and token (what the email should contain)
uid = urlsafe_base64_encode(force_bytes(user.pk))
token = default_token_generator.make_token(user)
reset_path = f'/accounts/reset/{uid}/{token}/'
reset_url = f'http://localhost:8000{reset_path}'
print('\nComputed password reset URL (what the email should contain):')
print(reset_url)

print('\nNote: password reset email templates used: registration/password_reset_email.html and registration/password_reset_subject.txt')
