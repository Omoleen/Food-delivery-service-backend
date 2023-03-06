from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'is_staff', 'is_active', 'role', 'wallet', 'date_joined']
    list_filter = ['email', 'is_staff', 'is_active', 'role', 'wallet', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'wallet')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone_number', 'password1', 'password2', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ['wallet',]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["email"]
        else:
            return []


@admin.register(Rider)
class RiderAdmin(UserAdmin):
    model = Rider
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'wallet', 'date_joined']
    list_filter = ['email', 'is_active', 'wallet', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'wallet')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'city', 'password1', 'password2', 'is_active')}
         ),
    )
    ordering = ('email',)
    readonly_fields = ['wallet',]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["email"]
        else:
            return []


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    model = Customer
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'wallet', 'date_joined']
    list_filter = ['email', 'is_active', 'wallet', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'wallet')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'is_active')}
         ),
    )
    ordering = ('email',)
    readonly_fields = ['wallet',]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["email"]
        else:
            return []


@admin.register(Vendor)
class VendorAdmin(UserAdmin):
    model = Vendor
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'wallet', 'date_joined']
    list_filter = ['email', 'is_active', 'wallet', 'date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'wallet')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'is_active')}
         ),
    )
    ordering = ('email',)
    readonly_fields = ['wallet']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["email"]
        else:
            return []


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
