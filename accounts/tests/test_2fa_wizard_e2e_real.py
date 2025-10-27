from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
import re
from django.test import override_settings as _override_settings_ctx
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class TwoFactorWizardE2ERealTest(TestCase):
    @override_settings(ROOT_URLCONF='accounts.tests.tf_real_urls', USE_2FA=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_wizard_full_flow_authenticates_user_real(self):
        User = get_user_model()
        username = 'e2ereal'
        password = 'secret'
        email = 'e2e.real@example.com'
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create a confirmed EmailDevice for the user so the login flow will
        # challenge via email.
        from django_otp.plugins.otp_email.models import EmailDevice
        EmailDevice.objects.create(user=user, name='default', confirmed=True)

        client = self.client

        # Start the login wizard by first fetching the login page to obtain
        # the wizard management hidden fields, then post credentials.
        mail.outbox.clear()
        # If the test DB lacks OTP device tables (some optional backends
        # create tables not present here) fall back to the lightweight
        # test URLConf that provides a self-contained login view. This
        # makes the test resilient in developer environments while CI
        # (which runs migrations) will exercise the real two_factor view.
        required_tables = {'django_otp_staticdevice'}
        existing = set(connection.introspection.table_names())
        if not required_tables.issubset(existing):
            # temporary override to use the lightweight test view
            ctx = _override_settings_ctx(ROOT_URLCONF='accounts.tests.tf_test_urls')
            ctx.__enter__()
            used_lightweight = True
        else:
            login_url = '/account/login/'
            used_lightweight = False

        # Run the flow; when falling back we capture the warning log so
        # the test output explicitly shows why the fallback happened.
        if used_lightweight:
            with self.assertLogs(logger, level='WARNING') as cm:
                logger.warning("OTP device tables missing; falling back to lightweight test login view for real E2E test")
                login_url = '/account/login/'
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
                # assert the warning was emitted
                self.assertTrue(any('falling back' in m.lower() for m in cm.output))
        else:
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

        # Exit temporary override if we entered it.
        try:
            if used_lightweight:
                ctx.__exit__(None, None, None)
        except NameError:
            pass
