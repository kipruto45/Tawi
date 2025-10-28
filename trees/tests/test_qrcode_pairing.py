import tempfile
import shutil
import os
from django.test import TestCase, override_settings
from django.utils import timezone

from beneficiaries.models import Beneficiary
from trees.models import Tree
from qrcodes.models import QRCode


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class QRCodeTreePairingTests(TestCase):
    def setUp(self):
        # create a beneficiary
        self.benef = Beneficiary.objects.create(name='Test School', type='school')

    def tearDown(self):
        # clean up any created files in MEDIA_ROOT
        try:
            from django.conf import settings
            root = getattr(settings, 'MEDIA_ROOT', None)
            if root and os.path.isdir(root):
                shutil.rmtree(root)
        except Exception:
            pass

    def test_tree_generates_qr_and_qrcode_links(self):
        today = timezone.now().date()
        tree = Tree.objects.create(tree_id='T-TEST-1', planting_date=today, beneficiary=self.benef)

        # Tree should have generated a qr_image during save
        self.assertTrue(bool(tree.qr_image and tree.qr_image.name), 'Tree.qr_image should be set after save')

        # Create a QRCode linked to this tree and generate its image
        qr = QRCode.objects.create(tree=tree, label='test-qr')
        qr.generate_image(base_url='')
        qr.save()

        self.assertTrue(bool(qr.image and qr.image.name), 'QRCode.image should be set after generate_image')
        # Ensure relation is set
        self.assertEqual(qr.tree.pk, tree.pk)

        # Deleting the Tree should set QRCode.tree to NULL (on_delete=SET_NULL)
        tree_pk = tree.pk
        tree.delete()
        qr.refresh_from_db()
        self.assertIsNone(qr.tree, 'QRCode.tree should be null after Tree deletion')

        # QRCode should still exist
        self.assertTrue(QRCode.objects.filter(pk=qr.pk).exists())

    def test_deleting_qrcode_does_not_delete_tree(self):
        today = timezone.now().date()
        tree = Tree.objects.create(tree_id='T-TEST-2', planting_date=today, beneficiary=self.benef)
        qr = QRCode.objects.create(tree=tree, label='test-qr-2')
        qr.generate_image(base_url='')
        qr.save()

        # Delete QRCode and ensure Tree still exists
        qr_pk = qr.pk
        qr.image.delete(save=False)
        qr.delete()
        self.assertFalse(QRCode.objects.filter(pk=qr_pk).exists())
        self.assertTrue(Tree.objects.filter(pk=tree.pk).exists(), 'Deleting QRCode should not delete linked Tree')
