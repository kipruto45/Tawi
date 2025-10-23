from django.test import TestCase
from django.contrib.auth import get_user_model
from dashboard.services.dashboard_service import get_dashboard_summary
from beneficiaries.models import Beneficiary
from trees.models import Tree, TreeSpecies


class DashboardServiceTest(TestCase):
    def setUp(self):
        sp = TreeSpecies.objects.create(name='Eucalyptus')
        ben = Beneficiary.objects.create(name='Test School', type='school')
        Tree.objects.create(tree_id='T1', species=sp, planting_date='2024-01-10', beneficiary=ben, number_of_seedlings=10, status='alive')
        Tree.objects.create(tree_id='T2', species=sp, planting_date='2024-02-15', beneficiary=ben, number_of_seedlings=5, status='dead')

    def test_summary_counts(self):
        summary = get_dashboard_summary()
        self.assertEqual(summary['total_trees'], 15)
        self.assertEqual(summary['alive'], 10)
        self.assertEqual(summary['dead'], 5)
