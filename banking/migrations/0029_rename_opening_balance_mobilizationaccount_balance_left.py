# Generated by Django 5.1.6 on 2025-03-31 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0028_mobilizationaccount_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobilizationaccount',
            old_name='opening_balance',
            new_name='balance_left',
        ),
    ]
