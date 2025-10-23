from django.core.management.base import BaseCommand
import os
import sys
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run initial setup: makemigrations, migrate, create a dev superuser if none exists.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
        parser.add_argument('--email', default='admin@example.com')
        parser.add_argument('--password', default='adminpass')

    def handle(self, *args, **options):
        self.stdout.write('Running makemigrations...')
        call_command('makemigrations')
        self.stdout.write('Applying migrations...')
        call_command('migrate')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(options['username'], options['email'], options['password'])
            self.stdout.write(self.style.SUCCESS(f"Superuser '{options['username']}' created."))
        else:
            self.stdout.write('Superuser already exists, skipping creation.')

        self.stdout.write('\nSetup complete. Next steps:')
        self.stdout.write('- Review `requirements.txt` and install production packages if needed:')
        self.stdout.write('  pip install -r requirements.txt')
        self.stdout.write('- For production, configure DATABASES in settings.py and a cache backend (Redis).')
        self.stdout.write('- Run the dev server: python manage.py runserver')
