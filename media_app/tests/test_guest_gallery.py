from django.test import Client, TestCase


class GuestMediaGalleryTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_guest_media_page_renders(self):
        resp = self.client.get('/media/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'gallery-container')
