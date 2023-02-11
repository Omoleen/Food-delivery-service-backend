# Generated by Django 4.1.4 on 2023-02-07 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_vendorprofile_business_email'),
        ('vendorapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='vendorapp.menucategory'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='quantity',
            field=models.CharField(choices=[('PER_WRAP', 'Per Wrap'), ('PER_SPOON', 'Per Spoon'), ('PER_PLATE', 'Per Plate')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='menucategory',
            unique_together={('user', 'name')},
        ),
    ]
