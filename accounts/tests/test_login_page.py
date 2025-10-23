from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse


User = get_user_model()


class LoginPageSmokeTest(TestCase):
    def test_login_page_renders(self):
        resp = self.client.get('/accounts/login/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Tawi Project')


class LoginBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass', role='admin')

    def test_role_based_redirect_admin(self):
        resp = self.client.post('/accounts/login/', {'username': 'u1', 'password': 'pass'})
        # should redirect (302) to admin dashboard
        self.assertEqual(resp.status_code, 302)

    def test_remember_me_sets_session_expiry(self):
        resp = self.client.post('/accounts/login/', {'username': 'u1', 'password': 'pass', 'remember': '1'})
        self.assertEqual(resp.status_code, 302)
        # session expiry should be the configured value
        expiry = settings.LOGIN_REMEMBER_SECONDS
        # session expiry age is stored on the session object
        self.assertEqual(self.client.session.get_expiry_age(), expiry)

    def test_group_based_fallback_redirect(self):
        # create a new user without a role and add to Field Officers group
        u2 = User.objects.create_user(username='u2', password='pass')
        grp, _ = Group.objects.get_or_create(name='Field Officers')
        u2.groups.add(grp)
        resp = self.client.post('/accounts/login/', {'username': 'u2', 'password': 'pass'})
        self.assertEqual(resp.status_code, 302)

    def test_partner_role_redirect(self):
        # partner by role should go to partner dashboard
        p = User.objects.create_user(username='p1', password='pass', role='partner')
        resp = self.client.post('/accounts/login/', {'username': 'p1', 'password': 'pass'})
        self.assertEqual(resp.status_code, 302)

    def test_partner_group_fallback(self):
        # partner by group membership should go to partner dashboard
        p2 = User.objects.create_user(username='p2', password='pass')
        grp, _ = Group.objects.get_or_create(name='Partners')
        p2.groups.add(grp)
        resp = self.client.post('/accounts/login/', {'username': 'p2', 'password': 'pass'})
        self.assertEqual(resp.status_code, 302)

    def test_project_manager_role_redirect(self):
        pm = User.objects.create_user(username='pm1', password='pass', role='project_manager')
        resp = self.client.post('/accounts/login/', {'username': 'pm1', 'password': 'pass'})
        self.assertEqual(resp.status_code, 302)

    def test_project_manager_group_fallback(self):
        pm2 = User.objects.create_user(username='pm2', password='pass')
        grp, _ = Group.objects.get_or_create(name='Project Managers')
        pm2.groups.add(grp)
        resp = self.client.post('/accounts/login/', {'username': 'pm2', 'password': 'pass'})
        self.assertEqual(resp.status_code, 302)
