# Generated by Django 4.2.20 on 2025-03-11 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
