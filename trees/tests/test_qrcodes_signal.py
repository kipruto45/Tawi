from django.test import TestCase
from beneficiaries.models import Beneficiary, PlantingSite
from django.contrib.auth import get_user_model

from trees.models import Tree
from qrcodes.models import QRCode


class QRCodeSignalTests(TestCase):
    def setUp(self):
        self.benef = Beneficiary.objects.create(name='B', type='school')

    def test_qrcode_created_on_tree_save(self):
        t = Tree.objects.create(tree_id='T1', planting_date='2020-01-01', beneficiary=self.benef)
        # after save signal, QRCode should exist
        q = QRCode.objects.filter(tree=t).first()
        self.assertIsNotNone(q)
        # image should have been generated (or at least the field exists)
        self.assertTrue(q.image.name)
