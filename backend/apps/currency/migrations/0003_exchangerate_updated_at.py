# Generated by Django 5.1.3 on 2024-12-01 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0002_alter_exchangerate_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangerate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
