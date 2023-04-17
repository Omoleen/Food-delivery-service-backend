# Generated by Django 4.1.4 on 2023-04-17 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_webhookspaymentmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhookspaymentmessage',
            name='message',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='webhookspaymentmessage',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]