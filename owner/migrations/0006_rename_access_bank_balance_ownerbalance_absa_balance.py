# Generated by Django 5.1.6 on 2025-05-07 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0005_alter_ownerbalance_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ownerbalance',
            old_name='access_bank_balance',
            new_name='absa_balance',
        ),
    ]
