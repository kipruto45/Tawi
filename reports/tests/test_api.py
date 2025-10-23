from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from reports.models import GeneratedReport


class ReportsAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('tester', 'tester@example.com', 'pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_generate_creates_report_and_file(self):
        url = '/api/reports/generated/generate/'
        resp = self.client.post(url, {'name': 'Test Report', 'report_type': 'summary'}, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('id', data)
        rpt = GeneratedReport.objects.get(pk=data['id'])
        # file should be set (we store JSON snapshot)
        self.assertTrue(rpt.file)

    def test_download_pdf_and_xlsx_endpoints(self):
        # create report record
        rpt = GeneratedReport.objects.create(name='R2')
        gen_url = f'/api/reports/generated/{rpt.pk}/download_pdf/'
        resp = self.client.post(gen_url)
        self.assertEqual(resp.status_code, 200)
        j = resp.json()
        self.assertIn('url', j)
        gen_url2 = f'/api/reports/generated/{rpt.pk}/download_xlsx/'
        resp2 = self.client.post(gen_url2)
        self.assertEqual(resp2.status_code, 200)
        j2 = resp2.json()
        self.assertIn('url', j2)
