from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trees', '0001_initial'),
        ('media_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreeCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('target', models.PositiveIntegerField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='tree',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='trees.treecampaign'),
        ),
        migrations.AddField(
            model_name='tree',
            name='cause_of_death',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='tree',
            name='replaced_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replacements', to='trees.tree'),
        ),
        migrations.AddField(
            model_name='tree',
            name='replaced_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='treeupdate',
            name='canopy_cm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='treeupdate',
            name='diameter_cm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='treeupdate',
            name='media',
            field=models.ManyToManyField(blank=True, to='media_app.Media'),
        ),
    ]
