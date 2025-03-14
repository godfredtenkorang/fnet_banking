# Generated by Django 5.1.6 on 2025-03-02 20:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0015_alter_customercomplain_date'),
        ('users', '0011_alter_branch_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HoldCustomerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_phone', models.CharField(max_length=10)),
                ('agent_number', models.CharField(max_length=10)),
                ('transaction_id', models.CharField(max_length=100)),
                ('reasons', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.agent')),
            ],
        ),
    ]
