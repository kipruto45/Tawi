from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create (or update) an Admins group and grant common admin permissions.'

    def add_arguments(self, parser):
        parser.add_argument('--group', type=str, default='Admins', help='Name of the group to create or update')
        parser.add_argument('--perms', type=str, default='', help='Comma-separated list of permissions in app_label.codename format to grant (overrides defaults)')

    def handle(self, *args, **options):
        group_name = options['group']
        perms_arg = options.get('perms', '')

        # Default set of permissions to grant to admin group
        default_perms = [
            'beneficiaries.manage_sites',
            'dashboard.view_admin_dashboard',
            'trees.manage_trees',
        ]

        if perms_arg:
            perms = [p.strip() for p in perms_arg.split(',') if p.strip()]
        else:
            perms = default_perms

        # Create or get group
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created group '{group_name}'"))
        else:
            self.stdout.write(f"Using existing group '{group_name}'")

        added = []
        missing = []
        for p in perms:
            if '.' not in p:
                missing.append(p)
                continue
            app_label, codename = p.split('.', 1)
            # Try to find permission by codename and app_label
            perm = None
            try:
                # Try to find a matching content type for a model in app
                # Prefer explicit mapping for known perms
                mapping = {
                    'beneficiaries.manage_sites': ('beneficiaries', 'plantingsite'),
                    'dashboard.view_admin_dashboard': ('dashboard', 'dashboardconfig'),
                    'trees.manage_trees': ('trees', 'tree'),
                }
                if p in mapping:
                    ct_app, ct_model = mapping[p]
                    ct = ContentType.objects.filter(app_label=ct_app, model=ct_model).first()
                else:
                    ct = ContentType.objects.filter(app_label=app_label).first()

                if ct:
                    perm, _ = Permission.objects.get_or_create(codename=codename, content_type=ct, defaults={'name': codename})
                else:
                    # fallback: try to find permission by codename only
                    perm = Permission.objects.filter(codename=codename).first()

                if not perm:
                    missing.append(p)
                    continue

                group.permissions.add(perm)
                added.append(p)
            except Exception as exc:
                missing.append(p)

        group.save()

        if added:
            self.stdout.write(self.style.SUCCESS(f"Added permissions to '{group_name}': {', '.join(added)}"))
        if missing:
            self.stdout.write(self.style.WARNING(f"Could not find/create these permissions: {', '.join(missing)}"))
        self.stdout.write(self.style.SUCCESS('Done.'))
