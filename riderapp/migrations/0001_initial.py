# Generated by Django 4.1.4 on 2023-09-13 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RiderLoan',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False, unique=True)),
                ('request_date', models.DateField(auto_now_add=True)),
                ('loan_date', models.DateField(blank=True, null=True)),
                ('comment', models.CharField(blank=True, max_length=64, null=True)),
                ('repayment_end_date', models.DateField(blank=True, null=True)),
                ('loan_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(blank=True, choices=[('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('PENDING', 'Pending'), ('DECLINE', 'Decline')], default='PENDING', max_length=64, null=True)),
                ('purpose', models.CharField(blank=True, max_length=64, null=True)),
                ('repayment_plan', models.CharField(blank=True, choices=[('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly'), ('BIWEEKLY', 'BiWeekly')], max_length=64, null=True)),
                ('repayment_plan_period', models.IntegerField(default=0)),
                ('payment_missing', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RiderLoanPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_payed', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_before_payment', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_after_payment', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(blank=True, choices=[('PAID', 'paid'), ('PENDING', 'pending')], default='PENDING', max_length=64, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('repayment_plan', models.CharField(blank=True, max_length=64, null=True)),
                ('payment_source', models.CharField(blank=True, choices=[('WALLET', 'Wallet'), ('DEPOSIT', 'Deposit')], max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RiderWalletHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(blank=True, choices=[('PAYOUT', 'Payout'), ('DAILY_INCOME', 'Daily Income')], max_length=100, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
    ]
