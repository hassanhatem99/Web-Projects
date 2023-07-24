# Generated by Django 4.2 on 2023-06-26 11:15

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_comment_time_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='listing',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 11, 15, 58, 97150, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 26, 11, 15, 58, 92047, tzinfo=datetime.timezone.utc)),
        ),
    ]