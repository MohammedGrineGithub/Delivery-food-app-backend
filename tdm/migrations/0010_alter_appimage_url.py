# Generated by Django 5.1.2 on 2025-01-14 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tdm', '0009_alter_appimage_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appimage',
            name='url',
            field=models.TextField(blank=True),
        ),
    ]
