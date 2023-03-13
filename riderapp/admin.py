from django.contrib import admin
from .models import (RiderLoan,
                     RiderLoanPayment)

# Register your models here.
admin.site.register(RiderLoan)
admin.site.register(RiderLoanPayment)