from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class CustomLoginViewUnitTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='u_next', password='pw12345', role='volunteer')

    def test_post_with_explicit_next_in_post_is_respected(self):
        """POSTing to the login view with a 'next' should redirect to that URL."""
        login_path = reverse('login')
        # target to which we expect to be redirected
        target = reverse('dashboard_field')

        # Prepare POST data including next and credentials
        post_data = {'username': self.user.username, 'password': 'pw12345', 'next': target}

        # Use the test client to POST and assert redirect location.
        resp = self.client.post(login_path, post_data, follow=False)

        self.assertIn(resp.status_code, (302, 301))
        loc = resp.get('Location', '')
        self.assertTrue(loc.endswith(target), msg=f"Expected explicit next to be used, got redirect to {loc}")
