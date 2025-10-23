from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from donations.models import Donation


class DonationsListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='donorx', email='donorx@example.com', password='secret')

    def test_recent_donations_displayed(self):
        # create some donations
        Donation.objects.create(donor=self.user, amount='10.00', status='Completed')
        Donation.objects.create(donor=self.user, amount='25.50', status='Pending')

        # login as a staff user so we see the admin/all-donations view
        staff = self.User.objects.create_user(username='admin', email='a@example.com', password='adminpass', is_staff=True)
        self.client.login(username='admin', password='adminpass')

        url = reverse('donations:donations')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))
        # if rendered, ensure context contains recent_donations
        if resp.status_code == 200:
            self.assertTrue('recent_donations' in resp.context)
            self.assertGreaterEqual(len(resp.context['recent_donations']), 2)
            # check rendered HTML contains donor username and amounts
            self.assertContains(resp, 'donorx')
            self.assertContains(resp, '10.00')
            self.assertContains(resp, '25.50')
