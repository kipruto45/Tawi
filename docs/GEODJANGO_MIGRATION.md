GeoDjango / PostGIS Migration Plan

This project currently stores latitude/longitude as FloatFields for compatibility and easier testing. For production spatial features (distance queries, clustering, indexing) we recommend migrating to PostGIS and GeoDjango.

High-level steps:

1. Install Postgres and PostGIS on your server.
2. Ensure the Python environment has:
   - Psycopg2
   - Django with GIS support (GeoDjango)
   - libgdal and dependencies (platform-specific). See Django docs for OS-specific instructions.
3. Update `DATABASES` in `tawi_project/settings.py` to point to your Postgres database.
4. Add `django.contrib.gis` to `INSTALLED_APPS`.
5. Modify models: replace latitude/longitude with `PointField` (or keep both during a transition).
   - In this repo a `location = PointField(null=True, blank=True)` was added when GeoDjango is importable.
6. Create migrations. If changing field types on large tables consider:
   - Create a new `location` PointField, run `makemigrations` and `migrate`.
   - Backfill `location` from existing lat/lng with a migration or a management command.
   - Once `location` is populated, remove old lat/lng fields in a subsequent change.
7. Create PostGIS indexes (e.g. GIST index) in migrations:
   - `operations = [AddIndex(model_name='tree', index=GistIndex(fields=['location']))]`
8. Update queries to use GeoDjango querysets and distance lookups.

Notes:
- If you can't install system dependencies locally, you may use a staging server or Docker image with PostGIS to run migration tests.
- Always backup your DB before running large migrations.

Example backfill management command snippet:

from django.contrib.gis.geos import Point
from trees.models import Tree

for t in Tree.objects.exclude(latitude__isnull=True, longitude__isnull=True):
    t.location = Point(t.longitude, t.latitude)
    t.save()

