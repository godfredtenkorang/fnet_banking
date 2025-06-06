# Generated by Django 5.1.6 on 2025-04-28 12:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_remove_user_first_name_remove_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('OWNER', 'Owner'), ('BRANCH', 'Branch'), ('CUSTOMER', 'Customer'), ('MOBILIZATION', 'Mobilization'), ('DRIVER', 'Driver')], max_length=12),
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=10, null=True)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('company_number', models.CharField(blank=True, max_length=10, null=True)),
                ('digital_address', models.CharField(blank=True, max_length=50, null=True)),
                ('driver_code', models.CharField(blank=True, max_length=20, null=True)),
                ('driver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='driver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
