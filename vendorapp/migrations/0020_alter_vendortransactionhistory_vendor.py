# Generated by Django 4.1.4 on 2023-04-18 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_vendorridertransactionhistory'),
        ('vendorapp', '0019_alter_menuitem_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendortransactionhistory',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_transactions', to='users.vendor'),
        ),
    ]