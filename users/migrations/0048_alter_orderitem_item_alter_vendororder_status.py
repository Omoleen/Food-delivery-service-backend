# Generated by Django 4.1.4 on 2023-08-29 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_alter_customerorder_total_delivery_fee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='users.menuitem'),
        ),
        migrations.AlterField(
            model_name='vendororder',
            name='status',
            field=models.CharField(choices=[('REQUESTED', 'Requested'), ('CANCELLED', 'Cancelled'), ('ON_DELIVERY', 'On Delivery'), ('READY', 'Ready'), ('DELIVERED', 'Delivered'), ('IN_PROGRESS', 'In Progress'), ('DELIVERY_FAILED', 'Delivery Failed'), ('ACCEPT_DELIVERY', 'Accept Delivery')], default='REQUESTED', max_length=50),
        ),
    ]