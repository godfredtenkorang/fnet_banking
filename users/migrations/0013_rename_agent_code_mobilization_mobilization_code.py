# Generated by Django 5.1.6 on 2025-03-06 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_user_role_mobilization'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobilization',
            old_name='agent_code',
            new_name='mobilization_code',
        ),
    ]
