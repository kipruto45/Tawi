from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from beneficiaries.models import Beneficiary, PlantingSite
from trees.models import Tree
from django.utils import timezone


class LocationCRUDTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # client for requests
        self.client = Client()
        # admin user (staff)
        self.admin = User.objects.create_user(username='admin', email='admin@example.com', password='pass')
        self.admin.is_staff = True
        self.admin.save()

        # regular user
        self.user = User.objects.create_user(username='user', email='user@example.com', password='pass')

        # beneficiary and an initial site
        self.beneficiary = Beneficiary.objects.create(name='Benef', type='school')
        self.site = PlantingSite.objects.create(beneficiary=self.beneficiary, name='Site1', address='Addr', latitude=0.0, longitude=0.0)
        # create a Tree at the beneficiary so the site appears in the recent/future filter
        Tree.objects.create(tree_id='TEST-1', planting_date=timezone.localdate(), beneficiary=self.beneficiary)

    def test_public_list_shows_sites_and_hides_controls_for_anonymous(self):
        resp = self.client.get(reverse('locations:locations'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Site1')
        # anonymous should not see edit/delete links
        self.assertNotContains(resp, reverse('locations:edit_site', args=[self.site.id]))
        self.assertNotContains(resp, reverse('locations:delete_site', args=[self.site.id]))

    def test_admin_sees_controls_on_list(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('locations:locations'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, reverse('locations:edit_site', args=[self.site.id]))
        self.assertContains(resp, reverse('locations:delete_site', args=[self.site.id]))

    def test_admin_can_add_site(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('locations:add_site'))
        self.assertEqual(resp.status_code, 200)
        post_data = {
            'beneficiary': self.beneficiary.id,
            'name': 'NewSite',
            'address': 'New Addr',
            'latitude': '1.23',
            'longitude': '4.56',
            'notes': 'notes',
        }
        resp2 = self.client.post(reverse('locations:add_site'), post_data)
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(PlantingSite.objects.filter(name='NewSite').exists())

    def test_admin_can_edit_site(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.post(reverse('locations:edit_site', args=[self.site.id]), {
            'beneficiary': self.beneficiary.id,
            'name': 'Site1-updated',
            'address': self.site.address,
            'latitude': self.site.latitude,
            'longitude': self.site.longitude,
            'notes': '',
        })
        self.assertEqual(resp.status_code, 302)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, 'Site1-updated')

    def test_admin_can_delete_site(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.post(reverse('locations:delete_site', args=[self.site.id]))
        # delete view redirects back to location_map
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(PlantingSite.objects.filter(pk=self.site.id).exists())

    def test_non_admin_cannot_access_crud_views(self):
        self.client.login(username='user', password='pass')
        # add
        resp = self.client.get(reverse('locations:add_site'))
        self.assertEqual(resp.status_code, 302)
        # edit
        resp = self.client.get(reverse('locations:edit_site', args=[self.site.id]))
        self.assertEqual(resp.status_code, 302)
        # delete
        resp = self.client.post(reverse('locations:delete_site', args=[self.site.id]))
        self.assertEqual(resp.status_code, 302)
