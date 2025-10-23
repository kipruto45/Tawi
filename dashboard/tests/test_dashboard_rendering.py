from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class DashboardRenderingTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.pwd = 'testpass123'

    def _create_and_login(self, role):
        u = self.User.objects.create_user(username=f'u_{role}', password=self.pwd)
        u.role = role
        u.save()
        self.client.login(username=u.username, password=self.pwd)
        return u

    def test_field_dashboard_renders(self):
        self._create_and_login('field_officer')
        resp = self.client.get(reverse('dashboard_field'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('tasks', resp.context)

    def test_volunteer_dashboard_renders(self):
        self._create_and_login('volunteer')
        resp = self.client.get(reverse('dashboard_volunteer'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('tasks', resp.context)

    def test_partner_dashboard_renders(self):
        self._create_and_login('partner')
        resp = self.client.get(reverse('dashboard_partner'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('tasks', resp.context)

    def test_admin_dashboard_renders(self):
        self._create_and_login('admin')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('summary', resp.context)

    def test_guest_dashboard_renders_for_anonymous(self):
        resp = self.client.get(reverse('guest_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_trees', resp.context)
