# Generated by Django 5.0.2 on 2024-07-07 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_userbankaccount_initial_deposit_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bankrupt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bankrupt', models.BooleanField(default=False)),
            ],
        ),
    ]
