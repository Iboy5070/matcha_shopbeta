"""Helpers for purchase-order → warehouse receive."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum


@transaction.atomic
def create_import_from_po(po, *, employee=None, force: bool = False):
    """Create an Imports + ImportDetail rows from a PurchaseOrder.

    ImportDetail.save() bumps shop stock via receive_stock.
    Skips if this PO already has an import (unless force=True).
    Returns (import_obj | None, message).
    """
    from .models import Imports, ImportDetail, PurchaseOrder, _money

    if not po.pk:
        return None, "ໃບສັ່ງຊື້ຍັງບໍ່ໄດ້ບັນທຶກ"

    details = list(po.details.select_related("product").all())
    if not details:
        return None, f"PO #{po.id} ຍັງບໍ່ມີລາຍການສິນຄ້າ"

    existing = Imports.objects.filter(purchase_order=po).first()
    if existing and not force:
        return existing, f"PO #{po.id} ມີນຳເຂົ້າແລ້ວ (Import #{existing.id}) — ບໍ່ສ້າງຊ້ຳ"

    emp = employee if employee is not None else po.employee
    total = po.details.aggregate(s=Sum("subtotal"))["s"] or po.total_amount or Decimal("0.00")

    imp = Imports.objects.create(
        purchase_order=po,
        supplier=po.supplier,
        employee=emp,
        total_amount=_money(total),
    )
    for d in details:
        if d.quantity < 1:
            continue
        ImportDetail.objects.create(
            imports=imp,
            product=d.product,
            quantity=d.quantity,
            cost_price=d.cost_price,
        )

    if po.status != PurchaseOrder.Status.COMPLETED:
        PurchaseOrder.objects.filter(pk=po.pk).update(status=PurchaseOrder.Status.COMPLETED)

    imp.refresh_from_db()
    return imp, f"ສ້າງນຳເຂົ້າ Import #{imp.id} ຈາກ PO #{po.id} ແລ້ວ — ສະຕັອກເພີ່ມແລ້ວ"
