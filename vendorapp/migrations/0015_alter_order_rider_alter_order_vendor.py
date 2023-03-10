# Generated by Django 4.1.4 on 2023-03-13 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_riderprofile_amount_earned'),
        ('vendorapp', '0014_alter_order_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='rider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rider_orders', to='users.rider'),
        ),
        migrations.AlterField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor_orders', to='users.vendor'),
        ),
    ]
