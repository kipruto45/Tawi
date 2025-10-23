from django.test import TestCase, Client


class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_serves_landing(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<title>')
