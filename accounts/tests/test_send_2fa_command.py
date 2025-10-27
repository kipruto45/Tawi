from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
import re


class Send2FATestCommandTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="cmdtest", email="cmdtest@example.com", password="pass"
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', USE_2FA=True)
    def test_send_2fa_command_creates_and_sends_token(self):
        # Ensure no messages to start
        mail.outbox.clear()

        # Run the management command; use --create to ensure device exists
        call_command('send_2fa_test_email', self.user.username, '--create')

        # One message should have been sent
        self.assertGreaterEqual(len(mail.outbox), 1)
        msg = mail.outbox[-1]
        body = getattr(msg, 'body', str(msg))

        # Expect a 6-digit token in the body
        m = re.search(r"\b(\d{6})\b", body)
        self.assertIsNotNone(m, msg=f"No 6-digit token found in message body: {body}")

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', USE_2FA=True)
    def test_send_2fa_command_no_redact_flag_shows_token(self):
        """When --no-redact is passed and locmem is used, the command prints the full token."""
        mail.outbox.clear()
        from io import StringIO
        out = StringIO()
        call_command('send_2fa_test_email', self.user.username, '--create', '--no-redact', stdout=out)
        output = out.getvalue()
        # Expect a 6-digit token in the printed output
        self.assertRegex(output, r"\b\d{6}\b")
