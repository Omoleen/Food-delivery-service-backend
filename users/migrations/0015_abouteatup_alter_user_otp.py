# Generated by Django 4.1.4 on 2023-03-05 17:33

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_user_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutEatup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('instagram', models.URLField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('about', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='otp',
            field=models.IntegerField(default=48),
        ),
    ]
