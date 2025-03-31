# Generated by Django 5.1.6 on 2025-03-31 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0026_alter_customerpaymentatbank_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobilizationAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=20, unique=True)),
                ('opening_balance', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
