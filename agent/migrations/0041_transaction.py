# Generated by Django 5.1.6 on 2025-03-28 15:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0040_rename_report_branchreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('CASH_IN', 'Cash In'), ('CASH_OUT', 'Cash Out'), ('PAY_TO', 'Pay To')], max_length=10)),
                ('customer_phone', models.CharField(max_length=15)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_deposited', models.DateField(default=django.utils.timezone.now)),
                ('time_deposited', models.TimeField(default=django.utils.timezone.now)),
                ('reference', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
