# Generated by Django 4.1.4 on 2023-09-19 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customerapp', '0003_remove_customerdeliveryaddress_number_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomerTransactionHistory',
        ),
    ]
