# Generated by Django 4.1.4 on 2023-09-13 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customerapp', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertransactionhistory',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_transactions', to='users.customer'),
        ),
        migrations.AddField(
            model_name='customerdeliveryaddress',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_addresses', to='users.customer'),
        ),
        migrations.AlterUniqueTogether(
            name='customerdeliveryaddress',
            unique_together={('customer', 'label')},
        ),
    ]