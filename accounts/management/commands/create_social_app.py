from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Create or update an allauth SocialApp for Google using environment variables.'

    def add_arguments(self, parser):
        parser.add_argument('--provider', default='google', help='Provider slug, e.g. google')
        parser.add_argument('--name', default='Google', help='Display name for the SocialApp')

    def handle(self, *args, **options):
        provider = options['provider']
        name = options['name']

        try:
            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
        except Exception as e:
            self.stderr.write('django-allauth does not appear to be installed. Install and enable USE_ALLAUTH to use this command.')
            return

        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_SECRET')
        site_id = int(os.environ.get('SITE_ID', '1'))

        if not client_id or not secret:
            self.stderr.write('Environment variables GOOGLE_CLIENT_ID and GOOGLE_SECRET must be set.')
            return

        app, created = SocialApp.objects.update_or_create(
            provider=provider,
            defaults={'name': name, 'client_id': client_id, 'secret': secret}
        )

        # Ensure the app is attached to the current site
        try:
            site = Site.objects.get(pk=site_id)
        except Site.DoesNotExist:
            site = Site.objects.create(pk=site_id, domain='localhost', name='localhost')

        app.sites.set([site])
        app.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created SocialApp for provider {provider}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated SocialApp for provider {provider}'))
