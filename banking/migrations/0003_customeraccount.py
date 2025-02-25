# Generated by Django 5.1.6 on 2025-02-25 00:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0002_delete_customeraccount'),
        ('users', '0007_customer_date_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(blank=True, max_length=16)),
                ('account_name', models.CharField(blank=True, max_length=100)),
                ('bank', models.CharField(choices=[('Select bank', 'Select bank'), ('Access Bank', 'Access Bank'), ('Cal Bank', 'Cal Bank'), ('Fidelity Bank', 'Fidelity Bank'), ('Ecobank', 'Ecobank'), ('Adansi rural bank', 'Adansi rural bank'), ('Kwumawuman Bank', 'Kwumawuman Bank'), ('Pan Africa', 'Pan Africa'), ('SGSSB', 'SGSSB'), ('Atwima Rural Bank', 'Atwima Rural Bank'), ('Omnibsic Bank', 'Omnibsic Bank'), ('Omini bank', 'Omini bank'), ('Stanbic Bank', 'Stanbic Bank'), ('First Bank of Nigeria', 'First Bank of Nigeria'), ('Adehyeman Savings and loans', 'Adehyeman Savings and loans'), ('ARB Apex Bank Limited', 'ARB Apex Bank Limited'), ('Absa Bank', 'Absa Bank'), ('Agriculture Development bank', 'Agriculture Development bank'), ('Bank of Africa', 'Bank of Africa'), ('Bank of Ghana', 'Bank of Ghana'), ('Consolidated Bank Ghana', 'Consolidated Bank Ghana'), ('First Atlantic Bank', 'First Atlantic Bank'), ('First National Bank', 'First National Bank'), ('G-Money', 'G-Money'), ('GCB BanK LTD', 'GCB BanK LTD'), ('Ghana Pay', 'Ghana Pay'), ('GHL Bank Ltd', 'GHL Bank Ltd'), ('GT Bank', 'GT Bank'), ('National Investment Bank', 'National Investment Bank'), ('Opportunity International Savings And Loans', 'Opportunity International Savings And Loans'), ('Prudential Bank', 'Prudential Bank'), ('Republic Bank Ltd', 'Republic Bank Ltd'), ('Sahel Sahara Bank', 'Sahel Sahara Bank'), ('Sinapi Aba Savings and Loans', 'Sinapi Aba Savings and Loans'), ('Societe Generale Ghana Ltd', 'Societe Generale Ghana Ltd'), ('Standard Chartered', 'Standard Chartered'), ('universal Merchant Bank', 'universal Merchant Bank'), ('Zenith Bank', 'Zenith Bank'), ('Mtn', 'Mtn'), ('AirtelTigo', 'AirtelTigo'), ('Telecel', 'Telecel')], default='Access Bank', max_length=100)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer')),
            ],
        ),
    ]
