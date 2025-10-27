import unittest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import connection
import re


@unittest.skipUnless(connection.vendor == 'postgresql', 'Strict real 2FA integration test runs only on Postgres (CI).')
class TwoFactorIntegrationRealStrictTest(TestCase):
    @override_settings(ROOT_URLCONF='accounts.tests.tf_real_urls', USE_2FA=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_wizard_full_flow_authenticates_user_strict(self):
        """
        Run the real two_factor LoginView end-to-end without fallback.

        This test is intended to run in CI where the test database is
        Postgres and all migrations (including optional device tables) are
        applied. It will be skipped on SQLite/local developer environments.
        """
        # Ensure required OTP tables are present in the DB. Different
        # versions of django-otp produce slightly different table names
        # (e.g. 'django_otp_staticdevice' vs 'otp_static_staticdevice'), so
        # accept either form for the strict test.
        required_variants = [{'django_otp_staticdevice'}, {'otp_static_staticdevice'}]
        existing = set(connection.introspection.table_names())
        # pass if any variant is fully present
        if not any(variant.issubset(existing) for variant in required_variants):
            # report the canonical expected name variants for debugging
            self.fail(f"Required OTP tables missing for strict test: expected one of {required_variants}, existing={sorted(existing)}")

        User = get_user_model()
        username = 'strict_e2e'
        password = 'secret'
        email = 'strict_e2e@example.com'
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create a confirmed EmailDevice for the user so the login flow will
        # challenge via email.
        from django_otp.plugins.otp_email.models import EmailDevice
        EmailDevice.objects.create(user=user, name='default', confirmed=True)

        client = self.client

        mail.outbox.clear()
        login_url = '/account/login/'

        # GET then POST credentials (wizard management form fields needed)
        get_resp = client.get(login_url)
        self.assertEqual(get_resp.status_code, 200)
        # collect hidden inputs
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

        # collect management form fields from resp and post token
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
