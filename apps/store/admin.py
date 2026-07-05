from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Employee, Customer

@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ("emp_name", "emp_last", "user", "emp_tel")
    search_fields = ("emp_name", "emp_last", "emp_tel")

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("cus_name", "cus_last", "user", "cus_tel", "gender")
    search_fields = ("cus_name", "cus_last", "cus_tel")
