# Generated by Django 3.2.12 on 2024-05-30 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagemodel',
            name='title',
        ),
    ]
