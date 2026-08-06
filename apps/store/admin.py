from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminTextInputWidget
from .models import Employee, Customer


_ADDRESS_WIDGET = UnfoldAdminTextInputWidget()


class _SingleLineTextAdmin(ModelAdmin):
    """Render TextField address boxes as single-line inputs like other fields."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.TextField) and db_field.name in {
            "address",
            "emp_address",
            "sup_address",
        }:
            kwargs["widget"] = _ADDRESS_WIDGET
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Employee)
class EmployeeAdmin(_SingleLineTextAdmin):
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
class CustomerAdmin(_SingleLineTextAdmin):
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
