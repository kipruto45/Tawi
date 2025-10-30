from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import MessageSent


class MessagingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user('admin', 'admin@example.com', 'pass')
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()
        self.client = Client()

    def test_send_view_requires_login(self):
        url = reverse('core:message_send')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_admin_can_send_and_message_saved(self):
        self.client.login(username='admin', password='pass')
        url = reverse('core:message_send')
        resp = self.client.post(url, {'subject': 'Hi', 'body': 'Hello', 'recipients': 'custom', 'emails': 'a@example.com,b@example.com'})
        # should redirect to sent messages
        self.assertEqual(resp.status_code, 302)
        # message persisted
        ms = MessageSent.objects.first()
        self.assertIsNotNone(ms)
        self.assertEqual(ms.subject, 'Hi')
        self.assertEqual(ms.recipients_count, 2)
