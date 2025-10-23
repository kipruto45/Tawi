from django.test import TestCase
from django.urls import reverse


class RegisterIntegrationTests(TestCase):
    def test_register_redirects_to_login_with_role_message(self):
        url = reverse('register')
        data = {
            'username': 'newvol',
            'email': 'newvol@example.com',
            'role': 'volunteer',
            'password1': 'strong-pass-123',
            'password2': 'strong-pass-123',
        }
        resp = self.client.post(url, data, follow=True)
        # After successful registration we expect to be redirected to login
        self.assertEqual(resp.redirect_chain[-1][0], reverse('login'))
        # Check messages include the role label or the raw role string
        content = resp.content.decode('utf-8')
        self.assertIn('Role', content)
        self.assertIn('volunteer', content)
