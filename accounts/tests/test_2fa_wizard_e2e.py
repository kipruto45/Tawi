from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
import re
from unittest.mock import patch


class TwoFactorWizardE2ETest(TestCase):
    @override_settings(ROOT_URLCONF='accounts.tests.tf_test_urls', USE_2FA=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_wizard_full_flow_authenticates_user(self):
        User = get_user_model()
        username = 'e2euser'
        password = 'secret'
        email = 'e2e@example.com'
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create a confirmed EmailDevice for the user so the login flow will
        # challenge via email.
        from django_otp.plugins.otp_email.models import EmailDevice
        EmailDevice.objects.create(user=user, name='default', confirmed=True)

        client = self.client

        # Start the login wizard by first fetching the login page to obtain
        # the wizard management hidden fields, then post credentials.
        mail.outbox.clear()
        try:
            login_url = reverse('two_factor:login')
        except Exception:
            try:
                login_url = reverse('accounts:login')
            except Exception:
                login_url = '/account/login/'

        # Patch django_otp.devices_for_user so the two-factor wizard only
        # sees the EmailDevice we create. This avoids hitting missing tables
        # (e.g. static devices) in environments where those apps are not
        # present or their migrations were not applied.
        def _fake_devices_for_user(user, confirmed=True):
            from django_otp.plugins.otp_email.models import EmailDevice
            return EmailDevice.objects.filter(user=user, confirmed=confirmed)

        # Patch two_factor.utils.default_device so the wizard's token-step
        # detection returns our EmailDevice without enumerating all device
        # backends (which may reference tables that are not present in the
        # test DB). This avoids OperationalError from missing static device
        # tables.
        def _fake_default_device(user, confirmed=True):
            from django_otp.plugins.otp_email.models import EmailDevice
            return EmailDevice.objects.filter(user=user, confirmed=confirmed).first()

        with patch('two_factor.utils.default_device', _fake_default_device):
            get_resp = client.get(login_url)
            self.assertEqual(get_resp.status_code, 200)

            hidden_inputs = re.findall(r'<input[^>]+type="hidden"[^>]+>', get_resp.content.decode('utf-8'))
            initial_post = {}
            for inp in hidden_inputs:
                name_m = re.search(r'name="([^"]+)"', inp)
                val_m = re.search(r'value="([^"]*)"', inp)
                if name_m:
                    initial_post[name_m.group(1)] = val_m.group(1) if val_m else ''

            initial_post.update({'auth-username': username, 'auth-password': password})
            resp = client.post(login_url, initial_post, follow=True)
            self.assertEqual(resp.status_code, 200)

        # Verify an email was sent and extract the token
        self.assertTrue(mail.outbox, 'No email was sent during login challenge')
        body = mail.outbox[-1].body
        m = re.search(r"(\d{6,8})", body)
        self.assertIsNotNone(m, 'No numeric token found in email body')
        token = m.group(1)

        # Collect management form hidden fields from the response context if available
        post_data = {}
        try:
            wizard = resp.context['wizard']
            mgmt = wizard.management_form
            for name in mgmt.fields:
                try:
                    post_data[name] = mgmt[name].value()
                except Exception:
                    post_data[name] = mgmt.initial.get(name, '')
        except Exception:
            hidden_inputs = re.findall(r'<input[^>]+type="hidden"[^>]+>', resp.content.decode('utf-8'))
            for inp in hidden_inputs:
                name_m = re.search(r'name="([^"]+)"', inp)
                val_m = re.search(r'value="([^"]*)"', inp)
                if name_m:
                    post_data[name_m.group(1)] = val_m.group(1) if val_m else ''

        # Merge any remaining hidden inputs and set the token
        hidden_inputs_all = re.findall(r'<input[^>]+type="hidden"[^>]+>', resp.content.decode('utf-8'))
        for inp in hidden_inputs_all:
            name_m = re.search(r'name="([^"]+)"', inp)
            val_m = re.search(r'value="([^"]*)"', inp)
            if name_m and name_m.group(1) not in post_data:
                post_data[name_m.group(1)] = val_m.group(1) if val_m else ''

        post_data['token'] = token

        resp2 = client.post(login_url, post_data, follow=True)
        self.assertEqual(resp2.status_code, 200)
        user_after = resp2.wsgi_request.user
        self.assertTrue(user_after.is_authenticated)
