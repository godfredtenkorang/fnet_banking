# Generated by Django 5.1.6 on 2025-03-10 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilization', '0007_tellercalculator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_10',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_100',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_20',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_200',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_5',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='d_50',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tellercalculator',
            name='phone_number',
            field=models.CharField(max_length=13),
        ),
    ]
