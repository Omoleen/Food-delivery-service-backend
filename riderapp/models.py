from django.db import models
from users.models import Rider, RiderProfile
# Create your models here.
from datetime import datetime, timedelta
from datetime import date as Date
from dateutil.relativedelta import relativedelta


class RiderLoan(models.Model):
    class LoanStatusTypes(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        PENDING = 'PENDING', 'Pending'
        DECLINE = 'DECLINE', 'Decline'

    class RepaymentPlans(models.TextChoices):
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'
        BIWEEKLY = 'BIWEEKLY', 'BiWeekly'

    id = models.CharField(max_length=64, unique=True, primary_key=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='loans')
    request_date = models.DateField(auto_now_add=True)
    loan_date = models.DateField(null=True, blank=True)
    # next_repayment_date = models.DateField(null=True)
    comment = models.CharField(max_length=64, null=True, blank=True)
    repayment_end_date = models.DateField(null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=64, null=True, blank=True, choices=LoanStatusTypes.choices, default=LoanStatusTypes.PENDING)
    purpose = models.CharField(max_length=64, null=True, blank=True)
    repayment_plan = models.CharField(max_length=64, null=True, blank=True, choices=RepaymentPlans.choices)
    repayment_plan_period = models.IntegerField(default=0)
    payment_missing = models.BooleanField(default=False)

    def __str__(self):
        return f'Rider Loan - {self.id}'

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)

        # save original values, when model is loaded from database,
        # in a separate attribute on the model
        instance._loaded_values = dict(zip(field_names, values))

        return instance

    def save(self, *args, **kwargs):

        # check if a new db row is being added
        # When this happens the `_loaded_values` attribute will not be available
        if not self._state.adding:
            # check if field_1 is being updated
            if self._loaded_values['status'] == self.LoanStatusTypes.PENDING and self.status == self.LoanStatusTypes.ACTIVE:
                print('Create all the repayment plans')
                self.loan_date = Date.today()
                number_of_payments = self.repayment_plan_period
                # remainder = self.loan_amount % number_of_payments
                payment_amount = self.loan_amount / number_of_payments
                date = Date.today()
                payments = []
                before, after = self.loan_amount, 0
                for payment in range(self.repayment_plan_period):
                    if self.repayment_plan == self.RepaymentPlans.WEEKLY:
                        date += timedelta(weeks=1)
                    elif self.repayment_plan == self.RepaymentPlans.MONTHLY:
                        date += relativedelta(months=1)
                    elif self.repayment_plan == self.RepaymentPlans.BIWEEKLY:
                        date += timedelta(weeks=2)
                    after = before - payment_amount
                    payments.append(RiderLoanPayment(date=date,
                                                     amount=payment_amount,
                                                     rider_loan=self,
                                                     rider=self.rider,
                                                     amount_before_payment=before,
                                                     amount_after_payment=after,
                                                     repayment_plan=self.repayment_plan))
                    before = after
                RiderLoanPayment.objects.bulk_create(payments)
                print('Created payment plans')
                # TODO Create all the repayment plans

        super().save(*args, **kwargs)

    @property
    def next_repayment(self):
        plan = self.payments.filter(status=RiderLoanPayment.StatusTypes.PENDING).order_by('date').first()
        return plan


class RiderLoanPayment(models.Model):
    class PaymentSources(models.TextChoices):
        WALLET = 'WALLET', 'Wallet'
        DEPOSIT = 'DEPOSIT', 'Deposit'

    class StatusTypes(models.TextChoices):
        PAID = 'PAID', 'paid'
        PENDING = 'PENDING', 'pending'

    rider_loan = models.ForeignKey(RiderLoan, on_delete=models.CASCADE, related_name='payments')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='loan_payments')
    amount_payed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_before_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_after_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=64, null=True, blank=True, choices=StatusTypes.choices,
                              default=StatusTypes.PENDING)
    date = models.DateField(null=True, blank=True)
    repayment_plan = models.CharField(max_length=64, null=True, blank=True,)
    payment_source = models.CharField(max_length=64, null=True, blank=True, choices=PaymentSources.choices)

    def __str__(self):
        return f'{self.rider_loan} Payment Plan'


# class RiderWalletHistory(models.Model):
#     class TransactionTypes(models.TextChoices):
#         PAYOUT = 'PAYOUT', 'Payout'
#         DAILY_INCOME = 'DAILY_INCOME', 'Daily Income'
#
#     rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='rider_transactions')
#     comment = models.CharField(max_length=100, choices=TransactionTypes.choices, blank=True, null=True)
#     date_time = models.DateTimeField(auto_now_add=True)
#     amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
#
#     def __str__(self):
#         return f'{self.comment} - {self.date_time}'
