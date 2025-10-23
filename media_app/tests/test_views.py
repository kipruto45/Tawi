from django.test import TestCase, Client
from django.urls import reverse


class MediaViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_media_list_page(self):
        url = reverse('media_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
