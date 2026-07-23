from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Employee, Customer


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ("emp_name", "emp_last", "emp_tel", "user")
    search_fields = ("emp_name", "emp_last", "emp_tel")
    fieldsets = (
        ("ບັນຊີເຂົ້າລະບົບ", {
            "fields": ("user",),
            "description": "ເລືອກ User ທີ່ມີສິດ staff ເພື່ອໃຫ້ເຂົ້າ Staff / POS ໄດ້",
        }),
        ("ຂໍ້ມູນສ່ວນຕົວ", {
            "fields": ("emp_name", "emp_last", "emp_gender", "emp_tel", "emp_address"),
        }),
    )


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("cus_name", "cus_last", "cus_tel", "gender", "user")
    search_fields = ("cus_name", "cus_last", "cus_tel")
    fieldsets = (
        ("ຂໍ້ມູນລູກຄ້າ", {
            "fields": ("cus_name", "cus_last", "cus_tel", "gender", "address"),
            "description": "ຂໍ້ມູນສຳລັບຕິດຕໍ່ ແລະ ຈັດສົ່ງ",
        }),
        ("ບັນຊີເວັບ (ທາງເລືອກ)", {
            "fields": ("user",),
            "classes": ("collapse",),
        }),
    )
