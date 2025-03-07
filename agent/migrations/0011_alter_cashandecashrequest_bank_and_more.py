# Generated by Django 5.1.6 on 2025-02-28 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0010_alter_cashandecashrequest_bank_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashandecashrequest',
            name='bank',
            field=models.CharField(blank=True, choices=[('Select Bank', 'Select Bank'), ('Ecobank', 'Ecobank'), ('Fidelity', 'Fidelity'), ('Calbank', 'Calbank'), ('GTBank', 'GTBank'), ('Access Bank', 'Access Bank')], default='Select Bank', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashandecashrequest',
            name='network',
            field=models.CharField(blank=True, choices=[('Select Network', 'Select Network'), ('MTN', 'MTN'), ('Telecel', 'Telecel'), ('AirtelTigo', 'AirtelTigo')], default='Select Network', max_length=20, null=True),
        ),
    ]
