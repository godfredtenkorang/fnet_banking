# Generated by Django 5.1.6 on 2025-03-04 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0017_alter_customerpaymentatbank_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerpaymentatbank',
            name='total',
        ),
    ]
