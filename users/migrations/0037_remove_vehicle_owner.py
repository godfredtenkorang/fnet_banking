# Generated by Django 5.1.6 on 2025-05-08 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_vehicle_distance_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='owner',
        ),
    ]
