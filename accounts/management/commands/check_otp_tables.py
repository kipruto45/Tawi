from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Check that required django-otp/two_factor tables exist in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--required",
            nargs="*",
            default=['django_otp_staticdevice', 'otp_static_staticdevice', 'otp_email_emaildevice', 'two_factor_config'],
            help='List of table names that must exist (defaults cover common OTP tables).',
        )

    def handle(self, *args, **options):
        required = set(options.get('required') or [])
        tables = set(connection.introspection.table_names())

        missing = sorted(required - tables)
        if missing:
            raise CommandError(f"Required tables missing: {missing}. Ensure migrations ran and USE_2FA is enabled.")

        self.stdout.write(self.style.SUCCESS(f"All required tables present: {sorted(required)}"))
