from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class LoginIntegrationTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.users = {
            'admin': self.User.objects.create_user(username='int_admin', password='pass1234', role='admin'),
            'volunteer': self.User.objects.create_user(username='int_vol', password='pass1234', role='volunteer'),
            'field_officer': self.User.objects.create_user(username='int_field', password='pass1234', role='field_officer'),
        }

    def test_login_form_redirects_to_role_dashboard(self):
        for role, user in self.users.items():
            with self.subTest(role=role):
                login_url = reverse('login')
                resp = self.client.post(login_url, {'username': user.username, 'password': 'pass1234'}, follow=False)
                # we expect a redirect
                self.assertIn(resp.status_code, (302, 301))
                loc = resp.get('Location', '')
                # ensure the Location ends with the expected dashboard path
                expected = reverse({'admin': 'admin_dashboard', 'volunteer': 'dashboard_volunteer', 'field_officer': 'dashboard_field'}[role])
                self.assertTrue(loc.endswith(expected), msg=f'Login for role {role} redirect to {loc}, expected end with {expected}')

    def test_login_respects_next_parameter(self):
        # create a protected page; reuse dashboard_field as example
        target = reverse('dashboard_field')
        login_url = reverse('login') + f'?next={target}'
        user = self.users['field_officer']
        resp = self.client.post(login_url, {'username': user.username, 'password': 'pass1234'}, follow=False)
        self.assertIn(resp.status_code, (302, 301))
        loc = resp.get('Location', '')
        self.assertTrue(loc.endswith(target), msg=f'Expected next to be respected, got {loc}')
