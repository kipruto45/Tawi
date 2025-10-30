from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TaskAssignTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        # admin user
        self.admin = self.User.objects.create_user(username='t_admin', password='pw', role='admin')
        # volunteer
        self.vol = self.User.objects.create_user(username='t_vol', password='pw', role='volunteer')

    def test_admin_can_view_task_add(self):
        self.client.login(username='t_admin', password='pw')
        url = reverse('dashboard:task_add')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_admin_can_create_task(self):
        from ..models import Task
        self.client.login(username='t_admin', password='pw')
        url = reverse('dashboard:task_add')
        data = {
            'name': 'New Task',
            'description': 'Do something',
            'assigned_to': self.vol.id,
            'location': 'Park',
        }
        resp = self.client.post(url, data)
        # should redirect back to admin dashboard
        self.assertIn(resp.status_code, (302, 303))
        self.assertEqual(Task.objects.filter(name='New Task').count(), 1)

    def test_non_admin_cannot_access(self):
        self.client.login(username='t_vol', password='pw')
        url = reverse('dashboard:task_add')
        resp = self.client.get(url)
        # role_required returns 403 for authenticated but unauthorized
        self.assertEqual(resp.status_code, 403)
