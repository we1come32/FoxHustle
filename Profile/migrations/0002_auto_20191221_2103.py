# Generated by Django 3.0 on 2019-12-21 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
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
        migrations.DeleteModel(
            name='AccessProfile',
        ),
        migrations.AddField(
            model_name='profile',
            name='patronymic',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='surname',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='tester',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='userType',
            field=models.CharField(choices=[('AD', 'Admin'), ('TS', 'Tester'), ('US', 'User'), ('MD', 'Moderator'), ('HP', 'Helper')], default='US', max_length=9),
        ),
        migrations.AddField(
            model_name='profile',
            name='verifery',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='perms',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Profile.Permission'),
            preserve_default=False,
        ),
    ]
