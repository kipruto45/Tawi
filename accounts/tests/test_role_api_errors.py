from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

import json

class RoleAPIErrorTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin', is_staff=True, is_superuser=True)
        self.user = User.objects.create_user(username='alice', password='pass', role='volunteer')
        self.client = Client()

    def test_role_check_malformed_json(self):
        # send badly formed JSON
        res = self.client.post(reverse('api_role_check'), b'{"username": "alice", "role":', content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data['exists'])
        self.assertFalse(data['matches'])
        self.assertIsNone(data['user_role'])

    def test_change_role_invalid_role(self):
        self.client.login(username='admin', password='pass')
        res = self.client.post(reverse('api_change_role'), json.dumps({'username': 'alice', 'role': 'not_a_role'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn('invalid role', data.get('detail', '').lower())
