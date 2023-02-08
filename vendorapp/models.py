from django.db import models
from users.models import Vendor, VendorProfile


# MENU - START -
class MenuCategory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.vendor} - {self.name} Category'

    class Meta:
        unique_together = ('vendor', 'name',)


class MenuItem(models.Model):

    class QuantityType(models.TextChoices):
        PER_WRAP = "PER_WRAP", 'Per Wrap'
        PER_SPOON = "PER_SPOON", 'Per Spoon'
        PER_PLATE = "PER_PLATE", 'Per Plate'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    summary = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items', null=True)
    quantity = models.CharField(max_length=64, choices=QuantityType.choices, null=True)
    image = models.ImageField(upload_to='vendor/menu_item/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return f'{self.category} - {self.name} item'

    class Meta:
        unique_together = ('category', 'name',)


class MenuSubItem(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='subitems')
    name = models.CharField(max_length=64)
    max_items = models.IntegerField(default=0)
    items = models.JSONField(default=list)

    def __str__(self):
        return f'{self.item} - {self.name} sub item'

    class Meta:
        unique_together = ('item', 'name',)

# MENU - END -


class VendorTransactionHistory(models.Model):

    class QuantityType(models.TextChoices):
        PAYOUT = "PAYOUT", 'payout'
        INCOME = "INCOME", 'income'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=54, null=True, blank=True)
    comment = models.CharField(max_length=54, null=True, blank=True)
    under_review = models.DateTimeField(auto_now=True)
