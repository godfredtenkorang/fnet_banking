# Generated by Django 5.1.6 on 2025-04-28 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_alter_user_role_driver'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_number', models.CharField(max_length=20, unique=True)),
                ('model', models.CharField(max_length=50)),
                ('year', models.PositiveIntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.owner')),
            ],
        ),
    ]
