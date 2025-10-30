from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class LoginIntegrationTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        # Create a small set of users representing common roles used by the
        # login redirect logic. Assign a role attribute when possible.
        self.users = {}
        self.users['admin'] = self.User.objects.create_user(username='int_admin', password='pass1234')
        self.users['volunteer'] = self.User.objects.create_user(username='int_vol', password='pass1234')
        self.users['field_officer'] = self.User.objects.create_user(username='int_field', password='pass1234')
        self.users['partner'] = self.User.objects.create_user(username='int_partner', password='pass1234')
        # attempt to set role attributes if the model supports it
        for role, user in self.users.items():
            try:
                if role == 'admin':
                    user.role = 'admin'
                else:
                    user.role = role
                user.save()
            except Exception:
                # Some test user models may not expose a writable 'role' field in tests
                pass
        self.client = Client()

    def test_login_form_redirects_to_role_dashboard(self):
        mapping = {
            'admin': 'admin_dashboard',
            'volunteer': 'dashboard_volunteer',
            'field_officer': 'dashboard_field',
            'partner': 'dashboard_partner',
        }
        for role, user in self.users.items():
            with self.subTest(role=role):
                login_url = reverse('accounts:login')
                resp = self.client.post(login_url, {'username': user.username, 'password': 'pass1234'}, follow=False)
                # Expect a redirect after successful login (302)
                self.assertIn(resp.status_code, (302, 301))
                loc = resp.get('Location', '')
                # If a named route is used (e.g., admin_dashboard) ensure reverse works
                try:
                    expected = reverse(mapping[role])
                except Exception:
                    expected = mapping[role]
                self.assertTrue(loc.endswith(expected), msg=f'Login for role {role} redirected to {loc}, expected end with {expected}')

    def test_api_role_check_endpoint(self):
        # The role-check API should return exists=False for unknown usernames
        url = reverse('accounts:api_role_check')
        resp = self.client.post(url, {'username': 'noone', 'role': 'volunteer'}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('exists'), False)

