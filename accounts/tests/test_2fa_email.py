from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail


class Email2FATest(TestCase):
    @override_settings(USE_2FA=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_device_sends_token_and_verifies(self):
        User = get_user_model()
        user = User.objects.create_user(username='emailuser', email='emailuser@example.com', password='pass')

        # Import here so Django settings are configured
        from django_otp.plugins.otp_email.models import EmailDevice

        # Ensure no emails sent yet
        mail.outbox.clear()

        # Create device (unconfirmed initially)
        device = EmailDevice.objects.create(user=user, name='default', confirmed=False)

        # Generate a challenge which should send an email
        device.generate_challenge()

        # One message should be in the outbox
        self.assertTrue(len(mail.outbox) >= 1, 'No email was sent for email device challenge')

        # Extract token from outbox (token is included in body)
        body = mail.outbox[-1].body
        # Find first 6+ digit token in body
        import re
        m = re.search(r"(\d{6,8})", body)
        self.assertIsNotNone(m, 'No numeric token found in email body')
        token = m.group(1)

        # Device should verify the token
        self.assertTrue(device.verify_token(token))
