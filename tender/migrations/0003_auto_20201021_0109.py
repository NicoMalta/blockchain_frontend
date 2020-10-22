# Generated by Django 3.0.3 on 2020-10-21 01:09

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tender', '0002_opentendering'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenderfile',
            name='id',
        ),
        migrations.AlterField(
            model_name='tenderfile',
            name='hash',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
