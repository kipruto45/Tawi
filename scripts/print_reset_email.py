from django.conf import settings
import django.core.mail as mail
from django.contrib.auth.forms import PasswordResetForm

# Use locmem backend to capture the email
settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

email = 'tawiproject@gmail.com'
form = PasswordResetForm({'email': email})
if form.is_valid():
    form.save(domain_override='localhost:8000', use_https=False, from_email=settings.DEFAULT_FROM_EMAIL, email_template_name='registration/password_reset_email.html', subject_template_name='registration/password_reset_subject.txt')

print('OUTBOX LENGTH:', len(mail.outbox))
if mail.outbox:
    msg = mail.outbox[-1]
    print('SUBJECT:', msg.subject)
    print('\nBODY:\n')
    print(msg.body)
else:
    print('No messages in outbox')
