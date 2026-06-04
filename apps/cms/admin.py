from django.contrib import admin
from .models import Testimonial, FAQItem, ContactMessage


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("company_name", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question_th", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    readonly_fields = ("created_at",)
