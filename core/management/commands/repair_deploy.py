import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Safe deploy helper: runs migrate, collectstatic and then deploy_healthcheck. Opt-in only.'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Run commands with --noinput where supported')
        parser.add_argument('--email-test', action='store_true', help='Run deploy_healthcheck with --email-test')
        parser.add_argument('--email-to', help='Email address for healthcheck email test')

    def handle(self, *args, **options):
        self.stdout.write('Starting repair_deploy sequence...')

        noinput = options.get('noinput')

        # 1) Apply migrations
        try:
            self.stdout.write('Running migrations...')
            if noinput:
                call_command('migrate', '--noinput')
            else:
                call_command('migrate')
            self.stdout.write('Migrations complete')
        except Exception as e:
            self.stderr.write(f'ERROR running migrations: {e}')
            return

        # 2) Collect static
        try:
            self.stdout.write('Collecting static files...')
            if noinput:
                call_command('collectstatic', '--noinput')
            else:
                call_command('collectstatic')
            self.stdout.write('Collectstatic complete')
        except Exception as e:
            self.stderr.write(f'ERROR running collectstatic: {e}')
            return

        # 3) Run healthcheck
        try:
            self.stdout.write('Running deploy_healthcheck...')
            args = []
            if options.get('email_test'):
                args.append('--email-test')
                if options.get('email_to'):
                    args.extend(['--email-to', options.get('email_to')])
            call_command('deploy_healthcheck', *args)
        except Exception as e:
            self.stderr.write(f'ERROR running deploy_healthcheck: {e}')
            return

        self.stdout.write('repair_deploy sequence complete.')
