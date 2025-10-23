from django.test import TestCase, Client
from django.urls import reverse


class InsightsViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_insights_dashboard_accessible(self):
        """GET the insights dashboard and expect a 200 OK response."""
        url = reverse('insights_dashboard')
        resp = self.client.get(url)
        # The view should render successfully (200)
        self.assertEqual(resp.status_code, 200)
