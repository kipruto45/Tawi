from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Partner


class PartnerTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user('admin2', 'admin2@example.com', 'pass')
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()
        self.client = Client()

    def test_partner_add_get(self):
        self.client.login(username='admin2', password='pass')
        url = reverse('core:partner_add')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_partner_add_post_creates(self):
        self.client.login(username='admin2', password='pass')
        url = reverse('core:partner_add')
        resp = self.client.post(url, {'name': 'New Partner', 'contact_name': 'Joe', 'contact_email': 'joe@example.com'})
        self.assertEqual(resp.status_code, 302)
        p = Partner.objects.filter(name='New Partner').first()
        self.assertIsNotNone(p)
        self.assertEqual(p.contact_name, 'Joe')
