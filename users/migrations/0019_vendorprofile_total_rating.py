# Generated by Django 4.1.4 on 2023-03-10 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_vendorprofile_average_star_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='total_rating',
            field=models.IntegerField(default=0),
        ),
    ]