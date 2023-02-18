# Generated by Django 4.1.4 on 2023-02-18 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0007_alter_orderitem_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('REQUESTED', 'Requested'), ('CANCELLED', 'Cancelled'), ('ON_DELIVERY', 'On Delivery'), ('DELIVERED', 'Delivered'), ('IN_PROGRESS', 'In Progress')], default='REQUESTED', max_length=50),
        ),
    ]
