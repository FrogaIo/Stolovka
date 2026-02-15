from django.contrib import admin
from .models import Payment, Order, PurchaseRequest, Report

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_type', 'status', 'payment_date')
    list_filter = ('status', 'payment_type', 'payment_date')
    search_fields = ('user__name', 'receipt_number')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_type', 'status', 'created_at')
    list_filter = ('status', 'meal_type', 'date')
    search_fields = ('user__name',)

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product_name', 'created_by__name')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'start_date', 'end_date', 'created_by')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title', 'created_by__name')
