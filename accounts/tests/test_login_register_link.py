from django.test import TestCase


class LoginRegisterLinkTest(TestCase):
    def test_register_link_visible_to_anonymous(self):
        resp = self.client.get('/accounts/login/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Don't have an account? Register")