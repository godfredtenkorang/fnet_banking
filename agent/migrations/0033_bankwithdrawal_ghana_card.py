# Generated by Django 5.1.6 on 2025-03-19 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0032_alter_customerpayto_agent_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankwithdrawal',
            name='ghana_card',
            field=models.ImageField(blank=True, default='', null=True, upload_to='ghana_card/'),
        ),
    ]
