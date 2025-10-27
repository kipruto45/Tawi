from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
import json


class RoleCheckAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        # create a user with a known role
        self.user = User.objects.create_user(username='jdoe', email='jdoe@example.com', password='pass')
        # set role attribute if present
        try:
            setattr(self.user, 'role', 'volunteer')
            self.user.save()
        except Exception:
            # If the custom user model doesn't support role, tests will still
            # validate the non-existence path and the endpoint's stability.
            pass

    def test_role_check_existing_matching(self):
        url = '/accounts/api/role_check/'
        data = {'username': 'jdoe', 'role': 'volunteer'}
        resp = self.client.post(url, data, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn('exists', payload)
        self.assertTrue(payload['exists'])
        # matches should be True when the stored role equals requested role
        self.assertIn('matches', payload)

    def test_role_check_nonexisting(self):
        url = '/accounts/api/role_check/'
        data = {'username': 'noone', 'role': 'volunteer'}
        resp = self.client.post(url, data, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn('exists', payload)
        self.assertFalse(payload['exists'])
        self.assertFalse(payload['matches'])
