# Generated by Django 4.1.4 on 2023-09-19 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customertransactionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='close_hour',
            field=models.TimeField(blank=True, null=True, verbose_name='Close Hour'),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='open_hour',
            field=models.TimeField(blank=True, null=True, verbose_name='Open Hour'),
        ),
    ]