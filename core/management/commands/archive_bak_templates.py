import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Move *.bak template files under templates into templates/archive to avoid drift. Safe, reversible.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='List files that would be moved without moving them')

    def handle(self, *args, **options):
        base = Path.cwd()
        templates_dir = base / 'templates'
        if not templates_dir.exists():
            self.stdout.write('No templates directory found; nothing to do')
            return

        archive_root = templates_dir / 'archive_bak'
        archive_root.mkdir(exist_ok=True)

        moved = 0
        for p in templates_dir.rglob('*.bak'):
            # skip files already in archive
            if archive_root in p.parents:
                continue
            rel = p.relative_to(templates_dir)
            target = archive_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if options.get('dry_run'):
                self.stdout.write(f'Would move: {p} -> {target}')
            else:
                shutil.move(str(p), str(target))
                self.stdout.write(f'Moved: {p} -> {target}')
                moved += 1

        if not options.get('dry_run'):
            self.stdout.write(f'Archive complete, moved {moved} files to {archive_root}')
