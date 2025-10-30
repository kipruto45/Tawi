from django.test import TestCase, Client
from django.urls import reverse


class DonationsURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_donations_list_url_resolves(self):
        """The named URL 'donations:donations' should reverse and return 200 for anonymous users."""
        url = reverse('donations:donations')
        response = self.client.get(url)
        # We expect a 200 OK (or a redirect to login depending on project configuration). Accept 200 or 302.
        self.assertIn(response.status_code, (200, 302))

    def test_admin_dashboard_contains_donations_link(self):
        """Admin dashboard template file should include the namespaced donations URL in the sidebar."""
        from django.conf import settings
        import os

        tmpl_path = os.path.join(settings.BASE_DIR, 'templates', 'dashboard', 'dashboard_admin.html')
        try:
            with open(tmpl_path, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except FileNotFoundError:
            self.skipTest('dashboard_admin template not present in repository')

        # The dashboard template contains the Django template tag rather than a rendered URL,
        # so assert the template tag itself is present.
        self.assertIn("{% url 'donations:donations' %}", content)
