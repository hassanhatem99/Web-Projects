# Generated by Django 4.2.4 on 2023-12-29 19:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialVerse', '0007_alter_comment_time_created_alter_post_time_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 29, 19, 40, 56, 71033, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 29, 19, 40, 56, 69038, tzinfo=datetime.timezone.utc)),
        ),
    ]
