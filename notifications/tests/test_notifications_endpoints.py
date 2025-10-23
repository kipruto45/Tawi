from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from notifications.models import Notification

class NotificationsEndpointTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='alice', password='pass')
        self.client = Client()
        # create some notifications
        Notification.objects.create(recipient=self.user, verb='welcome', description='Welcome!', unread=True)
        Notification.objects.create(recipient=self.user, verb='update', description='Update', unread=True)

    def test_mark_notification_requires_login(self):
        notif = Notification.objects.filter(recipient=self.user).first()
        res = self.client.post(reverse('notifications_mark', args=[notif.pk]))
        self.assertIn(res.status_code, (302, 401, 403))

    def test_mark_notification(self):
        self.client.login(username='alice', password='pass')
        notif = Notification.objects.filter(recipient=self.user).first()
        res = self.client.post(reverse('notifications_mark', args=[notif.pk]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        notif.refresh_from_db()
        self.assertFalse(notif.unread)

    def test_clear_notifications_requires_post(self):
        res = self.client.get(reverse('notifications_clear'))
        # should be redirected to login or forbidden
        self.assertIn(res.status_code, (302, 401, 403))

    def test_clear_notifications(self):
        self.client.login(username='alice', password='pass')
        res = self.client.post(reverse('notifications_clear'))
        # redirects back to page
        self.assertIn(res.status_code, (302, 200))
        self.assertEqual(Notification.objects.filter(recipient=self.user, unread=True).count(), 0)

    def test_unmark_notification(self):
        self.client.login(username='alice', password='pass')
        notif = Notification.objects.filter(recipient=self.user).first()
        # mark it first
        self.client.post(reverse('notifications_mark', args=[notif.pk]))
        notif.refresh_from_db()
        self.assertFalse(notif.unread)
        # now unmark
        res = self.client.post(reverse('notifications_unmark', args=[notif.pk]))
        self.assertEqual(res.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.unread)
