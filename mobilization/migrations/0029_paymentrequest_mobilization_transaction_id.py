# Generated by Django 5.1.6 on 2025-05-07 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilization', '0028_remove_paymentrequest_mobilization_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrequest',
            name='mobilization_transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
