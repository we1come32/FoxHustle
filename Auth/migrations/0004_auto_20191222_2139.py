# Generated by Django 3.0 on 2019-12-22 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0003_auto_20191221_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authapp',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]