# Generated by Django 4.1.4 on 2023-04-18 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_vendorridertransactionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorridertransactionhistory',
            name='comment',
            field=models.CharField(blank=True, max_length=54, null=True),
        ),
        migrations.AddField(
            model_name='vendorridertransactionhistory',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.order'),
        ),
    ]