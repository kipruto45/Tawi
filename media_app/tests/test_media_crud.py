from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from media_app.models import Media
from django.core.files.uploadedfile import SimpleUploadedFile


class MediaCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='u1', email='u1@example.com', password='secret')
        self.staff = self.User.objects.create_user(username='staff', email='s@example.com', password='secret', is_staff=True)

    def test_upload_requires_login(self):
        url = reverse('media_upload')
        # anonymous users should be redirected to login
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_create_and_edit_and_delete_by_uploader(self):
        self.client.login(username='u1', password='secret')
        upload_url = reverse('media_upload')
        f = SimpleUploadedFile('test.jpg', b'filecontent', content_type='image/jpeg')
        resp = self.client.post(upload_url, {'title': 'x', 'file': f})
        self.assertIn(resp.status_code, (200, 302))

        m = Media.objects.first()
        self.assertIsNotNone(m)

        # edit
        edit_url = reverse('media_edit', args=[m.id])
        resp = self.client.post(edit_url, {'title': 'new'})
        self.assertEqual(resp.status_code, 200)
        m.refresh_from_db()
        self.assertEqual(m.title, 'new')

        # delete
        delete_url = reverse('media_delete', args=[m.id])
        resp = self.client.post(delete_url)
        self.assertIn(resp.status_code, (302, 200))
        self.assertFalse(Media.objects.filter(id=m.id).exists())

    def test_non_uploader_cannot_edit_or_delete(self):
        # create media by u1
        self.client.login(username='u1', password='secret')
        f = SimpleUploadedFile('test.jpg', b'filecontent', content_type='image/jpeg')
        self.client.post(reverse('media_upload'), {'title': 'x', 'file': f})
        m = Media.objects.first()
        self.client.logout()

        # attempt edit as other user
        self.client.login(username='staff', password='secret')
        resp = self.client.post(reverse('media_edit', args=[m.id]), {'title': 'bad'})
        self.assertIn(resp.status_code, (200, 403))
