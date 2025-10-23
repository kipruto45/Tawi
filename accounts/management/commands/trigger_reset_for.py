from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a test user (if missing) and POST to password_reset to print the console email.'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='?', help='Email address to trigger reset for', default='tawiproject@gmail.com')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        if created:
            # Set an unusable password so reset is required
            user.set_unusable_password()
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user {email}'))
        else:
            self.stdout.write(self.style.NOTICE(f'User {email} already exists'))

        client = Client()
        url = reverse('password_reset')
        response = client.post(url, {'email': email})
        self.stdout.write(f'POST {url} returned status {response.status_code}')

        # Also directly use PasswordResetForm.save() to force sending the email
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            form.save(
                domain_override='localhost:8000',
                use_https=False,
                subject_template_name='registration/password_reset_subject.txt',
                email_template_name='registration/password_reset_email.html',
                from_email=settings.DEFAULT_FROM_EMAIL,
            )
            self.stdout.write(self.style.SUCCESS('Triggered PasswordResetForm.save(); check console output for the reset email and link.'))
        else:
            self.stdout.write(self.style.ERROR('PasswordResetForm invalid for email: %s' % email))
