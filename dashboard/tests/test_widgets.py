from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from dashboard.models import Task
try:
    from notifications.models import Notification
except Exception:
    Notification = None


User = get_user_model()


class DashboardWidgetsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='widgetuser', password='pass')
        # create a task
        try:
            Task.objects.create(name='Plant seedlings', assigned_to=self.user, location='Site A')
        except Exception:
            pass
        # create a notification if available
        if Notification is not None:
            try:
                Notification.objects.create(verb='Assigned task', description='You have a new task', recipient=self.user)
            except Exception:
                pass

    def test_field_dashboard_shows_tasks_and_notifications(self):
        self.client.login(username='widgetuser', password='pass')
        res = self.client.get(reverse('dashboard_field'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        # task name should be visible when tasks exist
        self.assertIn('Plant seedlings', content)
        # notification preview if notifications app present
        if Notification is not None:
            self.assertIn('Assigned task', content)
