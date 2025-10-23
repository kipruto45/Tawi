from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class RoleAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin', is_staff=True, is_superuser=True)
        self.user = User.objects.create_user(username='bob', password='pass', role='volunteer')
        self.client = Client()

    def test_role_check_existing_user(self):
        res = self.client.post(reverse('api_role_check'), {'username': 'bob', 'role': 'volunteer'}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['exists'])
        self.assertTrue(data['matches'])
        self.assertEqual(data['user_role'], 'volunteer')

    def test_role_check_nonexistent(self):
        res = self.client.post(reverse('api_role_check'), {'username': 'noone', 'role': 'guest'}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data['exists'])
        self.assertFalse(data['matches'])
        self.assertIsNone(data['user_role'])

    def test_change_role_requires_admin(self):
        # non-authenticated attempt
        res = self.client.post(reverse('api_change_role'), {'username': 'bob', 'role': 'field_officer'}, content_type='application/json')
        self.assertIn(res.status_code, (401, 403))

    def test_admin_can_change_role(self):
        self.client.login(username='admin', password='pass')
        res = self.client.post(reverse('api_change_role'), {'username': 'bob', 'role': 'field_officer'}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['role'], 'field_officer')
