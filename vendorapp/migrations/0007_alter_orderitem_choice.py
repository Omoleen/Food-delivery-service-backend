# Generated by Django 4.1.4 on 2023-02-11 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0006_order_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='choice',
            field=models.JSONField(null=True),
        ),
    ]
