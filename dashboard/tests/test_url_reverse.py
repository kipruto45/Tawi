from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class DashboardURLReverseTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_reverse_and_access_anonymous(self):
        """Anonymous client can reverse and GET key dashboard/report routes."""
        names = [
            ('dashboard:dashboard_field_officer', {}),
            ('dashboard:assigned_tasks', {}),
            ('dashboard:volunteers_list', {}),
            # top-level non-namespaced alias used in templates
            ('reports', {}),
        ]

        for name, kwargs in names:
            url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
            resp = self.client.get(url)
            self.assertIn(resp.status_code, (200, 302), msg=f"{name} returned {resp.status_code}")

    def test_reverse_and_access_logged_in(self):
        """Authenticated client can access same routes (smoke test)."""
        self.client.login(username='tester', password='pass')
        names = [
            ('dashboard:dashboard_field_officer', {}),
            ('dashboard:assigned_tasks', {}),
            ('dashboard:volunteers_list', {}),
            ('reports', {}),
        ]

        for name, kwargs in names:
            url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
            resp = self.client.get(url)
            # For logged-in users we expect the pages to be directly accessible
            # (HTTP 200). Use strict assertion to catch unexpected redirects.
            self.assertEqual(resp.status_code, 200, msg=f"{name} returned {resp.status_code}")

    def test_admin_dashboard_requires_login_and_allows_admin(self):
        """Anonymous users are redirected; admin users may access admin dashboard."""
        # anonymous should be redirected (login)
        url = reverse('dashboard:admin_dashboard')
        anon_resp = self.client.get(url)
        self.assertIn(anon_resp.status_code, (302, 401), msg=f"anonymous returned {anon_resp.status_code}")

        # create an admin user and mark as superuser/staff so permission check passes
        User = __import__('django.contrib.auth').contrib.auth.get_user_model()
        admin = User.objects.create_user(username='adminuser', password='adminpass')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        self.client.login(username='adminuser', password='adminpass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, msg=f"admin returned {resp.status_code}")
