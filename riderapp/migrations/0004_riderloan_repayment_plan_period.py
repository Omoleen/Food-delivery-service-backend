# Generated by Django 4.1.4 on 2023-03-10 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('riderapp', '0003_remove_riderloanpayment_source_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='riderloan',
            name='repayment_plan_period',
            field=models.IntegerField(default=0),
        ),
    ]
