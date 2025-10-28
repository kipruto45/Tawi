from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class RoleRedirectsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def _create_user(self, username, password, role):
        u = self.User.objects.create_user(username=username, password=password)
        u.role = role
        u.save()
        return u

    def test_roles_redirect_to_expected_dashboards(self):
        # mapping of role -> expected url name
        mapping = {
            'admin': 'dashboard:admin_dashboard',
            'field_officer': 'dashboard:dashboard_field',
            'field': 'dashboard:dashboard_field',
            'volunteer': 'dashboard:dashboard_volunteer',
            'beneficiary': 'dashboard:dashboard',
            'partner': 'dashboard:dashboard_partner',
            'partner_institution': 'dashboard:dashboard_partner',
            'guest': 'guest_dashboard',
            'community': 'dashboard:dashboard_community',
            'project_manager': 'dashboard:dashboard_project',
        }

        pwd = 'p@ssw0rd123'
        for role, url_name in mapping.items():
            username = f'user_{role}'
            user = self._create_user(username, pwd, role)

            resp = self.client.post(reverse('login'), {'username': username, 'password': pwd})
            # should be redirected (302) to the named dashboard route
            self.assertIn(resp.status_code, (302, 303))
            # Check the redirect resolves to the expected path name
            expected = reverse(url_name)
            # Some redirects may include the full domain, so use endswith
            location = resp.get('Location') or ''
            self.assertTrue(location.endswith(expected), msg=f"Role {role} redirected to {location}; expected {expected}")
