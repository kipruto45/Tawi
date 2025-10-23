from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

email = 'tawiproject@gmail.com'
User = get_user_model()
try:
    user = User.objects.get(email=email)
except User.DoesNotExist:
    print(f'User with email {email} does not exist')
    raise SystemExit(1)

uid = urlsafe_base64_encode(force_bytes(user.pk))
token = default_token_generator.make_token(user)
path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
url = f'http://localhost:8000{path}'
print('Password reset URL:')
print(url)
