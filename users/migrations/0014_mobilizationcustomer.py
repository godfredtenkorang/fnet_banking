# Generated by Django 5.1.6 on 2025-03-09 21:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_rename_agent_code_mobilization_mobilization_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobilizationCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=10, null=True)),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('customer_location', models.CharField(blank=True, max_length=100, null=True)),
                ('digital_address', models.CharField(blank=True, max_length=100, null=True)),
                ('id_type', models.CharField(blank=True, max_length=20, null=True)),
                ('id_number', models.CharField(blank=True, max_length=100, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('customer_picture', models.ImageField(default='', upload_to='customer_pic/')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.branch')),
                ('mobilization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.mobilization')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mobilizationcustomer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
