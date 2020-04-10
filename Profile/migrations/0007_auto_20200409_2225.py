# Generated by Django 3.0.5 on 2020-04-09 19:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0006_blockprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='tester',
            new_name='test',
        ),
        migrations.AddField(
            model_name='profile',
            name='online',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscriptions',
            field=models.ManyToManyField(related_name='subscribers', to='Profile.Profile'),
        ),
    ]