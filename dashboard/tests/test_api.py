from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from beneficiaries.models import Beneficiary
from trees.models import Tree, TreeSpecies


class DashboardAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('tester','t@test.com','testpass')
        sp = TreeSpecies.objects.create(name='Grevillea')
        ben = Beneficiary.objects.create(name='Community Group', type='community')
        Tree.objects.create(tree_id='G1', species=sp, planting_date='2024-03-01', beneficiary=ben, number_of_seedlings=20, status='alive')
        self.client = APIClient()
        self.client.login(username='tester', password='testpass')

    def test_summary_api(self):
        resp = self.client.get('/dashboard/api/summary/')
        self.assertEqual(resp.status_code, 200)
        json = resp.json()
        self.assertIn('status', json)
        self.assertIn('data', json)
