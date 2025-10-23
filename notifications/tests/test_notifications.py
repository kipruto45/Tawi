from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('nuser', 'n@example.com', 'pass')
        Notification.objects.create(recipient=self.user, verb='created', description='Test')

    def test_unread_default_and_mark_read(self):
        n = Notification.objects.filter(recipient=self.user).first()
        self.assertTrue(n.unread)
        n.mark_read()
        n.refresh_from_db()
        self.assertFalse(n.unread)
