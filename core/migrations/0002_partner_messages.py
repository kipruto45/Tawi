# Generated minimal migration to add Partner and MessageSent models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_name', models.CharField(max_length=255, blank=True)),
                ('contact_email', models.EmailField(max_length=254, blank=True)),
                ('address', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageSent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255, blank=True)),
                ('body', models.TextField(blank=True)),
                ('sender', models.CharField(max_length=255, blank=True)),
                ('recipients_count', models.PositiveIntegerField(default=0)),
                ('recipients_preview', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
