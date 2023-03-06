from django.db import models
from users.models import Rider, RiderProfile
# Create your models here.

# TODO Rider Loan Payments
# class RiderLoan(models.Model):
#     class LoanStatusTypes(models.TextChoices):
#         ACTIVE = 'ACTIVE', 'Active'
#         COMPLETED = 'COMPLETED', 'Completed'
#         PENDING = 'PENDING', 'Pending'
#         DECLINE = 'DECLINE', 'Decline'
#
#     class RepaymentPlans(models.TextChoices):
#         WEEKLY = 'WEEKLY', 'Weekly'
#         MONTHLY = 'MONTHLY', 'Monthly'
#         BIWEEKLY = 'BIWEEKLY', 'BiWeekly'
#
#     id = models.CharField(max_length=64, unique=True, primary_key=True)
#     rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='loans')
#     request_date = models.DateField(auto_now_add=True)
#     loan_date = models.DateField(null=True)
#     # next_repayment_date = models.DateField(null=True)
#     comment = models.CharField(max_length=64, null=True, blank=True)
#     repayment_end_date = models.DateField(null=True)
#     loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     status = models.CharField(max_length=64, null=True, blank=True, choices=LoanStatusTypes.choices, default=LoanStatusTypes.PENDING)
#     purpose = models.CharField(max_length=64, null=True, blank=True)
#     repayment_plan = models.CharField(max_length=64, null=True, blank=True, choices=RepaymentPlans.choices)
#     payment_missing = models.BooleanField(default=False)
#
#     @property
#     def next_repayment_date(self):
#         return
#
#
# class RiderLoanPayment(models.Model):
#     class Sources(models.TextChoices):
#         WALLET = 'WALLET', 'Wallet'
#         DEPOSIT = 'DEPOSIT', 'Deposit'
#
#     rider_loan = models.ForeignKey(RiderLoan, on_delete=models.CASCADE, related_name='payments')
#     rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='loan_payments')
#     amount_payed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     amount_before_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     amount_after_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     date = models.DateField(auto_now_add=True)
#     source = models.CharField(max_length=64, null=True, blank=True)
