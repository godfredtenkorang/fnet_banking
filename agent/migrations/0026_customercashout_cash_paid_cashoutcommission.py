# Generated by Django 5.1.6 on 2025-03-05 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0025_rename_amount_sent_customercashin_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='customercashout',
            name='cash_paid',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=19),
        ),
        migrations.CreateModel(
            name='CashOutCommission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('customer_cash_out', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cashoutcommissions', to='agent.customercashout')),
            ],
        ),
    ]
