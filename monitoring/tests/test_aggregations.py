from django.test import TestCase
from django.contrib.auth import get_user_model
from monitoring.models import MonitoringReport
from beneficiaries.models import PlantingSite


class MonitoringAggregationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('muser', 'm@example.com', 'pass')
        site = PlantingSite.objects.create(name='Site A', latitude=0.0, longitude=0.0)
        MonitoringReport.objects.create(site=site, reporter=self.user, total_planted=10, surviving=8)
        MonitoringReport.objects.create(site=site, reporter=self.user, total_planted=5, surviving=5)

    def test_survival_rate_property(self):
        qs = MonitoringReport.objects.all()
        rates = [r.survival_rate for r in qs]
        self.assertIn(80.0, rates)
        self.assertIn(100.0, rates)

    def test_average_survival_aggregation(self):
        from django.db.models import Avg, F
        qs = MonitoringReport.objects.all()
        avg = qs.aggregate(avg_rate=Avg((F('surviving') * 1.0) / F('total_planted') * 100))['avg_rate']
        self.assertIsNotNone(avg)
        self.assertAlmostEqual(round(avg, 1), 90.0, places=1)
