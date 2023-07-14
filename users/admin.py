from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin, OSMGeoAdmin):
    model = User
    list_display = ['email', 'is_staff', 'is_active', 'role', 'wallet', 'date_joined']
    list_filter = ['email', 'is_staff', 'is_active', 'role', 'wallet', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'wallet', 'role', 'location', 'location_lat', 'location_long', 'date_joined')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone_number', 'password1', 'password2')},
         ),
        ('Permissions', {'fields': ('is_active',)})
    )
    search_fields = ('email',)
    ordering = ('email',)
    # readonly_fields = ['wallet']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["email", 'date_joined', 'password', 'wallet']
        else:
            return ['date_joined']


@admin.register(Rider)
class RiderAdmin(CustomUserAdmin):
    model = Rider
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')},
         ),
        ('Permissions', {'fields': ('is_active',)})
    )


@admin.register(Customer)
class CustomerAdmin(CustomUserAdmin):
    model = Customer
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')},
         ),
        ('Permissions', {'fields': ('is_active',)})
    )


@admin.register(Vendor)
class VendorAdmin(CustomerAdmin):
    model = Vendor
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')},
         ),
        ('Permissions', {'fields': ('is_active',)})
    )


@admin.register(VerifyPhone)
class VerifyPhoneAdmin(admin.ModelAdmin):
    model = VerifyPhone
    list_display = ['user', 'phone_number', 'otp', 'is_verified']
    list_filter = ['is_verified']
    fieldsets = (
        (None, {'fields': ('user', 'phone_number', 'otp', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'phone_number', 'otp', 'is_verified')}
         ),
    )
    # readonly_fields = ['user', 'phone_number']
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['user', 'phone_number']
        else:
            return []


admin.site.register(Review)
admin.site.register(Notification)
admin.site.register(AboutEatup)
admin.site.register(BankAccount)
admin.site.register(VendorProfile)
admin.site.register(CustomerProfile)
admin.site.register(RiderProfile)
admin.site.register(WebhooksPaymentMessage)
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
admin.site.register(MenuSubItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(VendorRiderTransactionHistory)
