# Generated by Django 2.0.6 on 2020-04-13 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0012_permission_devlogsaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='img',
            field=models.CharField(default='/image/default.png', max_length=50),
        ),
    ]
