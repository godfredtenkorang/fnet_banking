# Generated by Django 5.1.6 on 2025-03-31 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0032_remove_mobilizationaccount_account_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mobilizationaccount',
            name='name',
        ),
    ]
