import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Run quick deploy health checks: DB connect, pending migrations, env vars, and optional test email.'

    def add_arguments(self, parser):
        parser.add_argument('--email-test', action='store_true', help='Attempt to send a test email using configured EMAIL settings')
        parser.add_argument('--email-to', help='Email address to send the test message to (requires --email-test)')

    def handle(self, *args, **options):
        self.stdout.write('Starting deploy healthcheck...')

        # 1) Check important environment variables
        self.stdout.write('\nChecking important environment variables:')
        important = ['SECRET_KEY', 'DATABASE_URL', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'DEFAULT_FROM_EMAIL']
        for name in important:
            val = os.environ.get(name)
            status = 'SET' if val else 'MISSING'
            self.stdout.write(f' - {name}: {status}')

        # 2) Database connectivity
        self.stdout.write('\nTesting database connectivity...')
        try:
            from django.db import connections
            conn = connections['default']
            conn.ensure_connection()
            self.stdout.write(' - Database: OK')
        except Exception as e:
            self.stdout.write(f' - Database: ERROR: {e}')

        # 3) Pending migrations (enhanced - will optionally auto-apply when opted-in)
        self.stdout.write('\nChecking for pending migrations...')
        try:
            from django.db import connections
            from django.db.migrations.executor import MigrationExecutor
            from django.core.management import call_command

            conn = connections['default']
            executor = MigrationExecutor(conn)
            targets = executor.loader.graph.leaf_nodes()
            plan = executor.migration_plan(targets)
            if plan:
                self.stdout.write(f' - Pending migrations: {len(plan)} (run manage.py migrate)')

                # Optional: auto-apply migrations if explicitly enabled via env var
                auto_apply = os.environ.get('AUTO_APPLY_MIGRATIONS') == '1'
                if auto_apply:
                    self.stdout.write(' - AUTO_APPLY_MIGRATIONS=1: applying migrations now...')
                    try:
                        call_command('migrate', '--noinput')
                        self.stdout.write(' - Migrations applied successfully')
                        # Recompute pending after applying
                        executor = MigrationExecutor(conn)
                        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
                        if plan:
                            self.stdout.write(f' - Pending migrations remaining: {len(plan)}')
                        else:
                            self.stdout.write(' - Pending migrations: none')
                    except Exception as me:
                        self.stdout.write(f' - ERROR applying migrations: {me}')
            else:
                self.stdout.write(' - Pending migrations: none')
        except Exception as e:
            self.stdout.write(f' - Pending migrations: ERROR while checking: {e}')

        # 4) Template load sanity check for dashboard templates referenced in errors
        self.stdout.write('\nChecking presence of key dashboard templates...')
        # check common dashboard templates (include a couple of name variants)
        tmpl_names = [
            'dashboard/dashboard_admin.html',
            'dashboard/dashboard_guest.html',
            'dashboard/dashboard_partner.html',
            'dashboard/dashboard_field.html',
            'dashboard/dashboard_volunteer.html',
            'dashboard/dashboard_projectmanager.html',
            'dashboard/dashboard_projectmanagement.html',
        ]
        from django.template.loader import get_template, TemplateDoesNotExist
        for t in tmpl_names:
            try:
                get_template(t)
                self.stdout.write(f' - {t}: present')
            except TemplateDoesNotExist:
                self.stdout.write(f' - {t}: MISSING')
            except Exception as e:
                self.stdout.write(f' - {t}: ERROR: {e}')
        # 5) Optional email test
        if options.get('email_test'):
            self.stdout.write('\nAttempting to send test email...')
            to_addr = options.get('email_to') or os.environ.get('DEPLOY_HEALTHCHECK_EMAIL') or os.environ.get('DEFAULT_FROM_EMAIL')
            if not to_addr:
                self.stdout.write(' - No recipient configured (use --email-to or set DEFAULT_FROM_EMAIL/DEPLOY_HEALTHCHECK_EMAIL)')
            else:
                try:
                    from django.core.mail import send_mail
                    send_mail('Deploy healthcheck', 'This is a test email from deploy_healthcheck.', settings.DEFAULT_FROM_EMAIL, [to_addr], fail_silently=False)
                    self.stdout.write(f' - Test email sent to {to_addr}')
                except Exception as e:
                    self.stdout.write(f' - Email send ERROR: {e}')

        self.stdout.write('\nDeploy healthcheck complete.')
