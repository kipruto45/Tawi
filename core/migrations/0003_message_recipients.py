# Migration to add MessageRecipient model
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_partner_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(max_length=50, default='pending')),
                ('error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='recipients', to='core.messagesent')),
            ],
        ),
    ]
