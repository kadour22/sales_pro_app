# Generated by Django 4.2.7 on 2025-06-29 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='api.salesfile')),
                ('sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='api.salesrecord')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
