from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class DashboardRoleAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # create role-specified users
        # create users and set their role at creation (supported by the custom
        # User model via extra fields)
        self.admin = User.objects.create_user(username='r_admin', password='pw', role='admin')
        self.field = User.objects.create_user(username='r_field', password='pw', role='field_officer')
        self.vol = User.objects.create_user(username='r_vol', password='pw', role='volunteer')
        self.partner = User.objects.create_user(username='r_partner', password='pw', role='partner')
        self.project = User.objects.create_user(username='r_proj', password='pw', role='project_manager')
        self.client = Client()

    def _assert_redirects_to_login(self, resp):
        self.assertIn(resp.status_code, (302, 301))

    def test_admin_access(self):
        url = reverse('admin_dashboard')
        # anonymous -> redirect to login
        resp = self.client.get(url)
        self._assert_redirects_to_login(resp)
    # non-admin -> forbidden (use POST login to exercise the login view)
    login_url = reverse('accounts:login')
    self.client.post(login_url, {'username': 'r_field', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
        self.client.logout()
    # admin -> ok
    self.client.post(login_url, {'username': 'r_admin', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_field_access(self):
        url = reverse('dashboard_field')
        resp = self.client.get(url)
        self._assert_redirects_to_login(resp)
    self.client.post(login_url, {'username': 'r_field', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    self.client.post(login_url, {'username': 'r_vol', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_volunteer_access(self):
        url = reverse('dashboard_volunteer')
        resp = self.client.get(url)
        self._assert_redirects_to_login(resp)
    self.client.post(login_url, {'username': 'r_vol', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # admin should also be allowed
    self.client.post(login_url, {'username': 'r_admin', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_partner_access(self):
        url = reverse('dashboard_partner')
        resp = self.client.get(url)
        self._assert_redirects_to_login(resp)
    self.client.post(login_url, {'username': 'r_partner', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    self.client.post(login_url, {'username': 'r_vol', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_project_access(self):
        url = reverse('dashboard_project')
        resp = self.client.get(url)
        self._assert_redirects_to_login(resp)
    self.client.post(login_url, {'username': 'r_proj', 'password': 'pw'})
    resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    self.client.post(login_url, {'username': 'r_admin', 'password': 'pw'})
    resp = self.client.get(url)
        # admin should also be allowed
        self.assertEqual(resp.status_code, 200)
