# Generated by Django 5.1.3 on 2024-12-01 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='exchangerate',
            unique_together={('currency_from', 'currency_to')},
        ),
        migrations.RemoveField(
            model_name='exchangerate',
            name='last_updated',
        ),
    ]