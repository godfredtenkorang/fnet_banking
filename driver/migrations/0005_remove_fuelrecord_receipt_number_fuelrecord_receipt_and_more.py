# Generated by Django 5.1.6 on 2025-04-28 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0004_expense'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fuelrecord',
            name='receipt_number',
        ),
        migrations.AddField(
            model_name='fuelrecord',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to='fuel_receipts/'),
        ),
        migrations.AlterField(
            model_name='mileagerecord',
            name='end_mileage',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
