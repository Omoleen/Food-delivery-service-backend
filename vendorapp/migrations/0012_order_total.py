# Generated by Django 4.1.4 on 2023-03-13 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0011_order_distance_order_pickup_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.FloatField(null=True),
        ),
    ]
