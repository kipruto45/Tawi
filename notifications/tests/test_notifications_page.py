from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notifications.models import Notification


class NotificationsPageTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='pageuser', email='pageuser@example.com', password='testpass')
        Notification.objects.create(recipient=self.user, verb='Hello', description='Welcome!')
        Notification.objects.create(recipient=self.user, verb='Reminder', description='Please submit your report')

    def test_notifications_page_shows_verb_and_description(self):
        self.client.login(username='pageuser', password='testpass')
        res = self.client.get(reverse('notifications_page'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn('Hello', content)
        self.assertIn('Welcome!', content)
        self.assertIn('Reminder', content)
        self.assertIn('Please submit your report', content)
