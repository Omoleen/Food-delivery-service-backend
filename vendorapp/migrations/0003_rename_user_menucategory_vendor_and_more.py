# Generated by Django 4.1.4 on 2023-02-08 01:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_vendorprofile_business_email'),
        ('vendorapp', '0002_alter_menuitem_category_alter_menuitem_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menucategory',
            old_name='user',
            new_name='vendor',
        ),
        migrations.AlterUniqueTogether(
            name='menucategory',
            unique_together={('vendor', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together={('category', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='menusubitem',
            unique_together={('item', 'name')},
        ),
    ]
