from django.db import migrations


def create_permission(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')

    ct, _ = ContentType.objects.get_or_create(app_label='dashboard', model='dashboardconfig')
    # create a permission codename 'view_admin_dashboard'
    Permission.objects.update_or_create(
        codename='view_admin_dashboard',
        content_type=ct,
        defaults={'name': 'Can view admin dashboard'},
    )


def remove_permission(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    Permission.objects.filter(codename='view_admin_dashboard').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_permission, remove_permission),
    ]
