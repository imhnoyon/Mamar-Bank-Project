# Generated by Django 5.0.2 on 2024-07-06 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_birth_day_userbankaccount_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbankaccount',
            name='initial_deposit_date',
            field=models.DateField(auto_created=True),
        ),
    ]