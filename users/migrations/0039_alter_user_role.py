# Generated by Django 4.1.4 on 2023-08-25 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('RIDER', 'Rider'), ('VENDOR', 'Vendor'), ('CUSTOMER', 'Customer'), ('VENDOR_EMPLOYEE', 'VendorEmployee')], default='ADMIN', max_length=50),
        ),
    ]