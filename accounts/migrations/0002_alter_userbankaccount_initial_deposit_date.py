# Generated by Django 5.0.2 on 2024-07-05 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbankaccount',
            name='initial_deposit_date',
            field=models.DateField(auto_created=True, blank=True),
        ),
    ]
