# Generated by Django 5.1.6 on 2025-03-13 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_picture',
            field=models.ImageField(blank=True, default='', null=True, upload_to='customer_pic/'),
        ),
    ]
