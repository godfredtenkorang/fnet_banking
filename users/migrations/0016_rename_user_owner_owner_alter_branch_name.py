# Generated by Django 5.1.6 on 2025-03-12 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_user_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='owner',
            old_name='user',
            new_name='owner',
        ),
        migrations.AlterField(
            model_name='branch',
            name='name',
            field=models.CharField(choices=[('DVLA', 'DVLA'), ('HEAD OFFICE', 'HEAD OFFICE'), ('KEJETIA', 'KEJETIA'), ('MELCOM SANTASI', 'MELCOM SANTASI'), ('MELCOM TANOSO', 'MELCOM TANOSO'), ('MELCOM MANHYIA', 'MELCOM MANHYIA'), ('MELCOM TAFO', 'MELCOM TAFO'), ('AHODWO MELCOM', 'AHODWO MELCOM'), ('ADUM MELCOM ANNEX', 'ADUM MELCOM ANNEX'), ('MELCOM SUAME', 'MELCOM SUAME'), ('KUMASI MALL MELCOM', 'KUMASI MALL MELCOM'), ('MOBILIZATION', 'MOBILIZATION')], max_length=100),
        ),
    ]
