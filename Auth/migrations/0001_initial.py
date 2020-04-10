# Generated by Django 3.0 on 2019-12-21 11:24

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='API_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5)),
                ('debug', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime.now)),
                ('end_date', models.DateTimeField(default=datetime.datetime.now)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AuthAccess', models.BooleanField(default=False)),
                ('AppsAccess', models.BooleanField(default=False)),
                ('BugtrackerAccess', models.BooleanField(default=False)),
                ('ExperienceAccess', models.BooleanField(default=False)),
                ('GoodsAccess', models.BooleanField(default=False)),
                ('GroupAccess', models.BooleanField(default=False)),
                ('PaymentAccess', models.BooleanField(default=False)),
                ('ProfileAccess', models.BooleanField(default=True)),
                ('MessageAccess', models.BooleanField(default=False)),
                ('SysAccess', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AuthInfoProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=255)),
                ('created_date', models.DateTimeField(default=datetime.datetime.now)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Profile.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='AuthApp',
            fields=[
                ('blocked', models.BooleanField(default=False)),
                ('blocked_date', models.DateTimeField(default=datetime.datetime.now)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('root', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Profile.Profile')),
                ('perms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auth.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auth.AuthApp')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Profile.Profile')),
            ],
        ),
    ]