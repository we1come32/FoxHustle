# Generated by Django 2.0.6 on 2020-04-13 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wall', '0004_auto_20200413_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='', max_length=40),
        ),
    ]
