# Generated by Django 5.1.2 on 2025-01-12 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tdm', '0008_alter_appimage_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appimage',
            name='url',
            field=models.TextField(),
        ),
    ]
