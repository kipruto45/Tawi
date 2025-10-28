from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from beneficiaries.models import Beneficiary, PlantingSite

User = get_user_model()


class LocationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create a beneficiary for site creation
        self.beneficiary = Beneficiary.objects.create(name='Test School', type='school')
        # normal user
        self.user = User.objects.create_user(username='user1', password='pass')
        # admin user
        self.admin = User.objects.create_user(username='admin1', password='pass')
        self.admin.is_staff = True
        self.admin.save()

    def test_public_locations_page_for_anonymous(self):
        res = self.client.get(reverse('locations:locations'))
        self.assertEqual(res.status_code, 200)
        # non-admin see the public template
        self.assertTemplateUsed(res, 'locations/user_location.html')

    def test_public_locations_page_for_regular_user(self):
        self.client.login(username='user1', password='pass')
        res = self.client.get(reverse('locations:locations'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'locations/user_location.html')

    def test_admin_sees_admin_template(self):
        self.client.login(username='admin1', password='pass')
        res = self.client.get(reverse('locations:locations'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'locations/location_map.html')

    def test_admin_can_add_edit_delete_site(self):
        self.client.login(username='admin1', password='pass')
        add_url = reverse('locations:add_site')
        data = {
            'beneficiary': self.beneficiary.pk,
            'name': 'Site A',
            'address': '123 Forest Rd',
            'latitude': 0.1,
            'longitude': 36.8,
            'notes': 'Test notes',
        }
        res = self.client.post(add_url, data)
        # should redirect back to locations map
        self.assertIn(res.status_code, (302, 301))
        site = PlantingSite.objects.filter(name='Site A').first()
        self.assertIsNotNone(site)

        # edit
        edit_url = reverse('locations:edit_site', args=[site.pk])
        res = self.client.post(edit_url, {'beneficiary': self.beneficiary.pk, 'name': 'Site A edited', 'address': 'Addr', 'latitude': 0.2, 'longitude': 36.9, 'notes': 'x'})
        self.assertIn(res.status_code, (302, 301))
        site.refresh_from_db()
        self.assertEqual(site.name, 'Site A edited')

        # delete
        delete_url = reverse('locations:delete_site', args=[site.pk])
        res = self.client.post(delete_url)
        self.assertIn(res.status_code, (302, 301))
        self.assertFalse(PlantingSite.objects.filter(pk=site.pk).exists())

    def test_non_admin_cannot_access_add_edit_delete(self):
        self.client.login(username='user1', password='pass')
        add_url = reverse('locations:add_site')
        res = self.client.get(add_url)
        # should redirect to login
        self.assertIn(res.status_code, (302, 301))

        # create a site as admin to test edit/delete
        site = PlantingSite.objects.create(beneficiary=self.beneficiary, name='Site B')
        edit_url = reverse('locations:edit_site', args=[site.pk])
        res = self.client.get(edit_url)
        self.assertIn(res.status_code, (302, 301))
        delete_url = reverse('locations:delete_site', args=[site.pk])
        res = self.client.get(delete_url)
        self.assertIn(res.status_code, (302, 301))

    def test_view_site_public(self):
        site = PlantingSite.objects.create(beneficiary=self.beneficiary, name='Public Site')
        res = self.client.get(reverse('locations:view_site', args=[site.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'locations/view_site.html')
*** End Patch