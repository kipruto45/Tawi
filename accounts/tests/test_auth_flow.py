from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthFlowTests(TestCase):
    def test_register_shows_role_and_redirects_to_login(self):
        register_url = reverse('register')
        data = {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'role': 'volunteer',
            'password1': 'ComplexPassw0rd!',
            'password2': 'ComplexPassw0rd!',
            # profile form expects nothing required (we render a ProfileForm with optional fields),
            # but the view expects profile form fields; the ProfileForm in code includes phone etc but not required
        }
        # Post registration: we now redirect to the login page with a success
        # message that includes the assigned role.
        resp = self.client.post(register_url, data)
        # Should redirect (302) to the login page
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])
        # Follow the redirect and check the flashed success message contains role
        resp2 = self.client.get(resp['Location'])
        self.assertContains(resp2, 'Registration complete')
        self.assertContains(resp2, 'Volunteer', msg_prefix="Role not displayed (case mismatch?)")

    def test_login_redirects_based_on_role(self):
        # Create a user with role 'admin' and log in
        u = User.objects.create_user(username='adminuser', email='admin@example.com', password='AdminPass123!')
        u.role = 'admin'
        u.save()

        login_url = reverse('login')
        resp = self.client.post(login_url, {'username': 'adminuser', 'password': 'AdminPass123!', 'role': 'admin'})
        # After successful login, should redirect to admin_dashboard
        # Django's LoginView redirects; follow redirect to get final URL
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('admin_dashboard'), resp['Location'])

        # Create a volunteer user and ensure redirect to volunteer dashboard
        v = User.objects.create_user(username='voluser', email='vol@example.com', password='VolPass123!')
        v.role = 'volunteer'
        v.save()
        resp2 = self.client.post(login_url, {'username': 'voluser', 'password': 'VolPass123!', 'role': 'volunteer'})
        self.assertEqual(resp2.status_code, 302)
        self.assertIn(reverse('dashboard_volunteer'), resp2['Location'])