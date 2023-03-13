# Generated by Django 4.1.4 on 2023-03-13 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0013_order_delivered_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(choices=[('PICKUP', 'pickup'), ('DELIVERY', 'delivery')], default='DELIVERY', max_length=20),
        ),
    ]