# Generated by Django 2.0.6 on 2020-04-13 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0016_auto_20200413_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]