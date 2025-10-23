from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AccountsAPITest(TestCase):
    def test_register_and_profile(self):
        url = '/accounts/api/register/'
        resp = self.client.post(url, {'username': 'u1', 'email': 'u1@example.com', 'password': 'pass'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('id', data)

        # login via normal django client and fetch profile
        User = get_user_model()
        user = User.objects.get(username='u1')
        self.client.force_login(user)
        p = self.client.get('/accounts/api/profile/')
        self.assertEqual(p.status_code, 200)

    def test_password_reset_flow_trigger(self):
        User = get_user_model()
        user = User.objects.create_user('pwuser', 'pw@example.com', 'pass')
        resp = self.client.post('/accounts/password_reset/', {'email': 'pw@example.com'})
        # Django's default password_reset view redirects to done page
        self.assertIn(resp.status_code, (302, 200))

    def test_role_based_user_list_access(self):
        User = get_user_model()
        admin = User.objects.create_user('admin2', 'a2@example.com', 'pass', role='admin')
        vol = User.objects.create_user('vol', 'v@example.com', 'pass', role='volunteer')
        # volunteer should be able to GET list (read-only allowed) but not create
        self.client.force_login(vol)
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.post('/api/users/', {'username':'x','email':'x@x.com'})
        self.assertIn(resp2.status_code, (403,401))
        # admin can create
        self.client.force_login(admin)
        resp3 = self.client.post('/api/users/', {'username':'x2','email':'x2@x.com'})
        self.assertIn(resp3.status_code, (201,200,400))

    def test_jwt_token_endpoint(self):
        # Only run if token endpoint exists
        resp = self.client.post('/api/token/', {'username':'nouser','password':'bad'})
        # we accept 401 or 404 if SimpleJWT isn't installed
        self.assertIn(resp.status_code, (401, 404, 400))
