# Generated by Django 4.2 on 2023-06-27 12:38

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_bid_time_created_alter_comment_time_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='time_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='comment',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 27, 12, 38, 3, 63545, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 27, 12, 38, 3, 57231, tzinfo=datetime.timezone.utc)),
        ),
    ]
