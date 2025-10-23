from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dashboard.models import Task
from django.utils import timezone


class DashboardTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='field1', password='pw', role='field_officer')

    def test_dashboard_field_renders_for_authenticated_user(self):
        # create a sample task
        Task.objects.create(name='Visit site', assigned_to=self.user, location='County A', status='pending', deadline=timezone.now().date())
        self.client.login(username='field1', password='pw')
        resp = self.client.get(reverse('dashboard_field'))
        self.assertEqual(resp.status_code, 200)
        # ensure template context variables are present
        self.assertIn('assigned_trees', resp.context)
        self.assertIn('tasks', resp.context)
        self.assertTrue(len(resp.context['tasks']) >= 1)

    def test_assigned_tasks_page_shows_user_tasks(self):
        Task.objects.create(name='Check seedlings', assigned_to=self.user, location='Site 1', status='done')
        self.client.login(username='field1', password='pw')
        resp = self.client.get(reverse('assigned_tasks'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Check seedlings')

    def test_dashboard_field_renders_for_anonymous(self):
        resp = self.client.get(reverse('dashboard_field'))
        self.assertEqual(resp.status_code, 200)
        # anonymous should still get context keys
        self.assertIn('assigned_trees', resp.context)
        self.assertIn('tasks', resp.context)
