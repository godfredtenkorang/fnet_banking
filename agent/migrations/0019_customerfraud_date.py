# Generated by Django 5.1.6 on 2025-03-02 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0018_customerfraud'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerfraud',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
