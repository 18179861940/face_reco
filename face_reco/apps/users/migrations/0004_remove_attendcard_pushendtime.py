# Generated by Django 3.0.5 on 2020-04-15 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendcard',
            name='pushEndTime',
        ),
    ]
