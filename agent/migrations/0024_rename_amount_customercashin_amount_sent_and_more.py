# Generated by Django 5.1.6 on 2025-03-05 13:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0023_alter_paymentrequest_created_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customercashin',
            old_name='amount',
            new_name='amount_sent',
        ),
        migrations.AddField(
            model_name='customercashin',
            name='cash_received',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=19),
        ),
        migrations.CreateModel(
            name='CashInCommission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('customer_cash_in', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cashincommissions', to='agent.customercashin')),
            ],
        ),
    ]
