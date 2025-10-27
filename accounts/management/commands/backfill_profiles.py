from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Create Profile objects for any User missing one. Safe and idempotent.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Report how many profiles would be created without creating them')

    def handle(self, *args, **options):
        User = get_user_model()
        created = 0
        checked = 0
        dry = options.get('dry_run', False)

        for u in User.objects.all():
            checked += 1
            try:
                _ = u.profile
            except Exception:
                if not dry:
                    try:
                        Profile.objects.get_or_create(user=u)
                        created += 1
                    except Exception as exc:
                        self.stderr.write(f"Failed to create profile for {u.username}: {exc}")
                else:
                    created += 1

        self.stdout.write(f"Checked {checked} users. Profiles to create/created: {created} (dry_run={dry})")
