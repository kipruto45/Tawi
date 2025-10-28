from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse


class AdminDashboardViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='adminuser', password='secret')
        # grant the dashboard view permission
        perm = Permission.objects.filter(codename='view_admin_dashboard').first()
        if perm:
            self.user.user_permissions.add(perm)
        self.user.save()

    def test_admin_dashboard_access_with_permission(self):
        login = self.client.login(username='adminuser', password='secret')
        self.assertTrue(login)
        # top-level alias exposed in tawi_project/urls.py
        url = reverse('admin_dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # check that a known piece of template text renders
        self.assertContains(resp, 'Admin Dashboard')
