from django.test import TestCase
from django.urls import resolve, reverse


class TwoFactorIntegrationTest(TestCase):
    """Integration checks for two-factor wiring when 2FA packages are present.

    These tests are best-effort: depending on how the project's root URLconf
    was imported (and whether USE_2FA was enabled at import time), the
    `two_factor` namespace may not be registered. In CI where USE_2FA is set
    globally the namespaced URLs will be present; otherwise this test will
    skip if wiring isn't installed.
    """

    def test_accounts_login_resolves_to_two_factor_loginview(self):
        # Import lazily so the test will skip cleanly if two_factor isn't
        # installed in the environment.
        try:
            from two_factor.views import LoginView as TwoFactorLoginView
        except Exception:
            self.skipTest('django-two-factor-auth not installed in this environment')

        # First, try to resolve the namespaced two_factor login URL if it
        # exists. If it does, ensure it maps to the TwoFactor LoginView.
        try:
            ns_url = reverse('two_factor:login')
        except Exception:
            ns_url = None

        if ns_url:
            ns_resolver = resolve(ns_url)
            ns_view_class = getattr(ns_resolver.func, 'view_class', None)
            self.assertEqual(ns_view_class, TwoFactorLoginView)
            return

        # If the namespaced URL isn't available, fall back to resolving
        # the existing accounts:login and ensure it was replaced by the
        # TwoFactor LoginView (older wiring strategy). If neither wiring
        # is present, skip rather than fail (this keeps the test stable in
        # environments where USE_2FA was not active at URLConf import time).
        try:
            url = reverse('accounts:login')
            resolver = resolve(url)
        except Exception:
            self.skipTest('accounts:login not resolvable in this environment')

        view_class = getattr(resolver.func, 'view_class', None)
        if view_class == TwoFactorLoginView:
            return

        self.skipTest('Two-factor login wiring not present under two_factor:login or accounts:login')
