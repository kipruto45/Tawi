from django.test import TestCase
from django.urls import reverse
from qrcodes.models import QRCode
from trees.models import Tree


class QRScanTest(TestCase):
    def setUp(self):
        t = Tree.objects.create(tree_id='T-100')
        self.qr = QRCode.objects.create(tree=t, label='TestQR')

    def test_increment_scan_via_view(self):
        url = reverse('qrcode-scan', kwargs={'pk': str(self.qr.pk)})
        resp = self.client.get(url)
        # after redirect or response, refresh and check scan_count
        self.qr.refresh_from_db()
        self.assertGreaterEqual(self.qr.scan_count, 1)
