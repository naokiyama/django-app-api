# Generated by Django 3.2.3 on 2021-06-01 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='tag',
            new_name='user',
        ),
    ]
