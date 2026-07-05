from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem, Bill, Payment, Reserved

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "order_date", "customer", "employee", "status")
    search_fields = ("customer__cus_name", "employee__emp_name")
    list_filter = ("status",)
    inlines = [OrderItemInline]

@admin.register(Bill)
class BillAdmin(ModelAdmin):
    list_display = ("id", "order", "bill_date", "total_amount", "paid_amount", "balance_due", "status")

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("id", "bill", "employee", "pay_amount", "pay_with", "pay_date")

@admin.register(Reserved)
class ReservedAdmin(ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "deposit_amount", "status")

