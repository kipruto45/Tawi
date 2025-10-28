from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class PostLoginRedirectTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        # mapping of role -> expected named url
        # For historical compatibility many templates/tests use un-namespaced
        # route names. Expect those top-level aliases here.
        self.role_map = {
            'admin': 'admin_dashboard',
            'field_officer': 'dashboard_field',
            'volunteer': 'dashboard_volunteer',
            'beneficiary': 'dashboard:dashboard',
            'partner': 'dashboard_partner',
            'guest': 'guest_dashboard',
            'project_manager': 'dashboard_project',
        }

    def _create_user(self, username, role):
        # create_user should accept role for the custom user model
        return self.User.objects.create_user(username=username, password='testpass123', role=role)

    def test_role_based_post_login_redirects(self):
        """Each role should be redirected to its corresponding dashboard."""
        for role, named_url in self.role_map.items():
            with self.subTest(role=role):
                username = f'user_{role}'
                user = self._create_user(username, role)
                # log the user in via the test client
                logged_in = self.client.login(username=username, password='testpass123')
                self.assertTrue(logged_in, msg=f'Could not log in user for role {role}')

                resp = self.client.get(reverse('accounts:post_login_redirect'))
                # The test client may return a relative or absolute Location header.
                # Accept either by checking the response Location ends with the
                # resolved path for the named URL.
                expected_path = reverse(named_url)
                self.assertEqual(resp.status_code, 302, msg=f'Expected redirect for role {role}')
                loc = resp.get('Location', '')
                self.assertTrue(loc.endswith(expected_path), msg=f"Redirect for role {role} went to {loc!r}, expected to end with {expected_path!r}")
