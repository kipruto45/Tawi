from django.test import TestCase


class GuestPagesSmokeTest(TestCase):
    """Simple smoke test that ensures important public/guest pages return 200.

    This prevents regressions where templates or views raise 500s during rendering.
    """

    def test_guest_pages_return_200(self):
        urls = [
            '/',
            '/trees/planted/',
            '/upcoming-events/',
            '/locations/',
            '/feedback/',
        ]
        for u in urls:
            with self.subTest(url=u):
                resp = self.client.get(u)
                self.assertEqual(resp.status_code, 200, f"{u} returned {resp.status_code}")
