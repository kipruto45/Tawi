from django.test import TestCase
from django.contrib.auth import get_user_model
from beneficiaries.models import Beneficiary
from django.core.files.uploadedfile import SimpleUploadedFile


class BulkImportTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client.force_login(self.admin)
        self.ben = Beneficiary.objects.create(name='BulkBen')

    def test_csv_dry_run(self):
        csv_content = 'tree_id,planting_date,beneficiary\nB1,2024-01-01,%d\nB2,2024-01-02,%d\n' % (self.ben.pk, self.ben.pk)
        f = SimpleUploadedFile('trees.csv', csv_content.encode('utf-8'), content_type='text/csv')
        resp = self.client.post('/api/trees/bulk_create/?dry_run=1', {'file': f})
        self.assertEqual(resp.status_code, 200)
        j = resp.json()
        self.assertTrue(j.get('valid'))
        self.assertEqual(j.get('rows_parsed'), 2)
