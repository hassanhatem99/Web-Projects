# Generated by Django 4.2.4 on 2023-12-29 19:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialVerse', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 29, 19, 2, 55, 922164, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 29, 19, 2, 55, 920256, tzinfo=datetime.timezone.utc)),
        ),
    ]