from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.widgets import UnfoldAdminTextareaWidget
from .models import Supplier, PurchaseOrder, PODetail, Imports, ImportDetail, Inventory


class _AutoCalcInlineMixin:
    """Readonly-looking money fields; JS + model.save() keep totals in sync."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield and db_field.name == "subtotal":
            formfield.widget.attrs["readonly"] = True
            formfield.help_text = "ອັດຕະໂນມັດ: ຈຳນວນ × ຕົ້ນທຶນ/ໜ່ວຍ"
        return formfield


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("sup_name", "sup_tel", "email")
    search_fields = ("sup_name", "sup_tel", "email")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.TextField) and db_field.name == "sup_address":
            kwargs["widget"] = UnfoldAdminTextareaWidget(attrs={"rows": 3})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ("ຜູ້ສະໜອງ", {
            "fields": ("sup_name", "sup_tel", "email", "sup_address"),
            "description": "ບໍລິສັດ/ຄົນທີ່ສົ່ງສິນຄ້າເຂົ້າຮ້ານ",
        }),
    )


class PODetailInline(_AutoCalcInlineMixin, TabularInline):
    model = PODetail
    extra = 1
    fields = ("product", "quantity", "cost_price", "subtotal")
    verbose_name_plural = "ລາຍການສິນຄ້າທີ່ສັ່ງ"


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ModelAdmin):
    list_display = ("id", "supplier", "employee", "po_date", "total_amount", "status", "import_count", "print_doc")
    list_filter = ("status",)
    actions = ["action_receive_into_stock"]
    inlines = [PODetailInline]
    fieldsets = (
        ("ໃບສັ່ງຊື້", {
            "fields": ("supplier", "employee", "total_amount", "status"),
            "description": (
                "ໃສ່ຈຳນວນ + ຕົ້ນທຶນ/ໜ່ວຍ — ລວມແຖວ ແລະ ຍອດລວມຄິດໄລ່ອັດຕະໂນມັດ. "
                "ເມື່ອປ່ຽນສະຖານະເປັນ «ສຳເລັດ» ລະບົບຈະສ້າງນຳເຂົ້າ + ເພີ່ມສະຕັອກອັດຕະໂນມັດ "
                "(ຫຼືເລືອກໃບສັ່ງ → Action «ຮັບເຂົ້າສາງອັດຕະໂນມັດ»). "
                "ພິມໃບກວດສອບ: ກົດລິ້ງ «ພິມ» ໃນຕາຕະລາງ"
            ),
        }),
    )

    class Media:
        js = ("admin/js/inventory_line_calc.js",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield and db_field.name == "total_amount":
            formfield.widget.attrs["readonly"] = True
            formfield.help_text = "ອັດຕະໂນມັດຈາກຜົນລວມທຸກແຖວ"
        return formfield

    @admin.display(description="ນຳເຂົ້າແລ້ວ")
    def import_count(self, obj):
        return obj.imports_set.count() if obj.pk else 0

    @admin.display(description="ໃບກວດສອບ")
    def print_doc(self, obj):
        if not obj.pk:
            return "—"
        url = reverse("staff_print_po", args=[obj.pk])
        return format_html('<a href="{}" target="_blank" rel="noopener">ພິມ</a>', url)

    @admin.action(description="ຮັບເຂົ້າສາງອັດຕະໂນມັດ (ສ້າງນຳເຂົ້າ + ເພີ່ມສະຕັອກ)")
    def action_receive_into_stock(self, request, queryset):
        from .po_receive import create_import_from_po

        ok, skip = 0, 0
        for po in queryset.select_related("supplier", "employee"):
            _imp, msg = create_import_from_po(po, employee=po.employee)
            if msg.startswith("ສ້າງນຳເຂົ້າ"):
                ok += 1
            else:
                skip += 1
                self.message_user(request, msg, level="WARNING")
        if ok:
            self.message_user(request, f"ຮັບເຂົ້າສາງສຳເລັດ {ok} ໃບສັ່ງ", level="SUCCESS")
        if skip and not ok:
            self.message_user(
                request,
                f"ຂ້າມ {skip} ໃບ (ມີນຳເຂົ້າແລ້ວ ຫຼື ບໍ່ມີລາຍການ)",
                level="WARNING",
            )

    def save_model(self, request, obj, form, change):
        prev_status = None
        if change and obj.pk:
            prev_status = (
                type(obj).objects.filter(pk=obj.pk).values_list("status", flat=True).first()
            )
        super().save_model(request, obj, form, change)
        obj._mz_should_auto_receive = obj.status == PurchaseOrder.Status.COMPLETED and (
            prev_status != PurchaseOrder.Status.COMPLETED
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        from django.db.models import Sum
        from decimal import Decimal

        total = obj.details.aggregate(s=Sum("subtotal"))["s"] or Decimal("0.00")
        if obj.total_amount != total:
            type(obj).objects.filter(pk=obj.pk).update(total_amount=total)
            obj.total_amount = total

        if obj.status == PurchaseOrder.Status.COMPLETED and obj.details.exists():
            from .po_receive import create_import_from_po

            # Transition to completed, OR completed PO that never got an import yet
            should = getattr(obj, "_mz_should_auto_receive", False) or (
                not Imports.objects.filter(purchase_order=obj).exists()
            )
            if should:
                _imp, msg = create_import_from_po(obj, employee=obj.employee)
                if msg.startswith("ສ້າງນຳເຂົ້າ"):
                    self.message_user(request, msg, level="SUCCESS")
                elif "ຍັງບໍ່ມີລາຍການ" in msg:
                    self.message_user(request, msg, level="WARNING")


class ImportDetailInline(_AutoCalcInlineMixin, TabularInline):
    model = ImportDetail
    extra = 1
    fields = ("product", "quantity", "cost_price", "subtotal")
    verbose_name_plural = "ລາຍການສິນຄ້າທີ່ຮັບເຂົ້າ"


@admin.register(Imports)
class ImportsAdmin(ModelAdmin):
    list_display = ("id", "purchase_order", "supplier", "employee", "imp_date", "total_amount", "print_doc")
    inlines = [ImportDetailInline]
    fieldsets = (
        ("ນຳເຂົ້າສິນຄ້າ", {
            "fields": ("purchase_order", "supplier", "employee", "total_amount"),
            "description": (
                "ປົກກະຕິບໍ່ຕ້ອງສ້າງມື: ໄປໃບສັ່ງຊື້ → ປ່ຽນເປັນ «ສຳເລັດ» ຫຼື Action «ຮັບເຂົ້າສາງອັດຕະໂນມັດ». "
                "ໜ້ານີ້ໃຊ້ເວລາຕ້ອງແກ້ດ້ວຍມື / ຮັບເຂົ້າຊ້ຳ. "
                "ພິມໃບກວດສອບ: ກົດລິ້ງ «ພິມ» ໃນຕາຕະລາງ"
            ),
        }),
    )

    class Media:
        js = ("admin/js/inventory_line_calc.js",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield and db_field.name == "total_amount":
            formfield.widget.attrs["readonly"] = True
            formfield.help_text = "ອັດຕະໂນມັດຈາກຜົນລວມທຸກແຖວ"
        return formfield

    @admin.display(description="ໃບກວດສອບ")
    def print_doc(self, obj):
        if not obj.pk:
            return "—"
        url = reverse("staff_print_import", args=[obj.pk])
        return format_html('<a href="{}" target="_blank" rel="noopener">ພິມ</a>', url)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        from django.db.models import Sum
        from decimal import Decimal
        total = obj.details.aggregate(s=Sum("subtotal"))["s"] or Decimal("0.00")
        if obj.total_amount != total:
            type(obj).objects.filter(pk=obj.pk).update(total_amount=total)


@admin.register(Inventory)
class InventoryAdmin(ModelAdmin):
    list_display = ("product", "batch_qty", "product_stock", "expiry_date", "created_at")
    list_filter = ("expiry_date", "product")
    search_fields = ("product__name",)
    ordering = ("-created_at",)
    fieldsets = (
        ("ຮັບສິນຄ້າເຂົ້າສາງ (+ສະຕັອກ)", {
            "fields": ("product", "quantity", "expiry_date"),
            "description": (
                "ໜ້ານີ້ = ປະຫວັດຮັບເຂົ້າ (1 ສິນຄ້າອາດມີຫຼາຍແຖວ). "
                "ຕົວເລກ «ຍອດຂາຍປັດຈຸບັນ» ຄືກັນທຸກແຖວຂອງສິນຄ້າດຽວກັນ. "
                "ພະນັກງານເພີ່ມສະຕັອກໄດ້ທີ່ /staff/inventory/ — ແກ້ຊື່/ລາຄາໃຫ້ Admin"
            ),
        }),
    )

    @admin.display(description="ເພີ່ມເຂົ້າຄັ້ງນີ້", ordering="quantity")
    def batch_qty(self, obj):
        return obj.quantity

    @admin.display(description="ຍອດຂາຍປັດຈຸບັນ (ທັງໝົດ)")
    def product_stock(self, obj):
        return obj.product.stock_qty if obj.product_id else "—"
