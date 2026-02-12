from django.contrib import admin
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "points")
    search_fields = ("name", "phone")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "cashier", "grand_total", "payment_method", "created_at")
    list_filter = ("payment_method", "created_at")
    search_fields = ("order_no", "cashier__username")
    inlines = [OrderItemInline]
