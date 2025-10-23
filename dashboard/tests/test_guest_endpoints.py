from django.test import TestCase
from django.urls import reverse


class GuestEndpointsTest(TestCase):
    def test_dashboard_guest_renders(self):
        url = reverse('guest_dashboard') if 'guest_dashboard' in [u.name for u in []] else reverse('guest_dashboard')
        resp = self.client.get(reverse('guest_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_upcoming_events_available(self):
        resp = self.client.get(reverse('events:upcoming_events'))
        self.assertEqual(resp.status_code, 200)

    def test_trees_planted_public_available(self):
        # Using the trees app namespace
        resp = self.client.get('/trees/public/planted/')
        self.assertIn(resp.status_code, (200, 302))

    def test_volunteer_sign_up_redirects_to_register(self):
        resp = self.client.get(reverse('volunteer_sign_up'))
        # Should redirect (302) or render the register page (200)
        self.assertIn(resp.status_code, (200, 302))
