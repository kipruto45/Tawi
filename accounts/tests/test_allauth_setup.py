from django.test import TestCase
import os


class AllAuthSetupTest(TestCase):
    """Simple test that verifies a Google SocialApp exists when creds are
    provided. This test is skipped when GOOGLE_CLIENT_ID/GOOGLE_SECRET are
    not present to avoid requiring external secrets in CI.
    """

    def test_google_socialapp_present_if_env(self):
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_SECRET')
        if not client_id or not secret:
            self.skipTest('GOOGLE_CLIENT_ID/GOOGLE_SECRET not set; skipping SocialApp presence test')

        try:
            from allauth.socialaccount.models import SocialApp
        except Exception:
            self.fail('django-allauth not installed or not enabled')

        apps = SocialApp.objects.filter(provider='google')
        self.assertTrue(apps.exists(), 'Expected a Google SocialApp to exist when GOOGLE_* env vars are set')
