# Generated by Django 3.0.5 on 2020-10-29 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockchainaccount',
            name='dni',
            field=models.CharField(max_length=200, null=True),
        ),
    ]