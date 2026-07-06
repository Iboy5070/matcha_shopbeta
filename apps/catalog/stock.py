"""Stock (inventory) helpers shared by web checkout, POS, staff verification,
and restocking.

Kept separate from models.py to avoid a circular import: Order/Reserved
(apps.sales) already import Product (apps.catalog), so apps.catalog cannot
import apps.sales at module load time. Functions here import apps.sales /
apps.inventory lazily inside the function body instead.

Stock timeline:
- Checkout (web or POS) only CHECKS availability — it does not remove stock
  yet, except POS "buy now" which is staff-entered directly with no later
  confirmation step, so it deducts immediately.
- Web "buy now" orders only lose stock once staff approves the payment
  slip (see apps.sales.staff_views.verify_slip).
- Reservations never touch stock at creation (they may be pure backorders).
  When new stock arrives, the newest pending reservations are earmarked
  first (stock_qty is reserved, but the physical batch is untouched).
  The earmark is only turned into a real batch deduction once staff marks
  the reservation complete (customer picked up + paid the rest), and is
  released back to the pool if staff cancels it instead.
"""

from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest

from .models import Product


def check_stock(cart_items) -> list:
    """cart_items: iterable of dicts with 'product' and 'qty'.

    Returns the list of items that do NOT have enough stock for a
    "buy now" purchase (empty list = all good). Reservations skip this
    check entirely — a reservation is allowed even at zero stock."""
    insufficient = []
    for item in cart_items:
        product = item["product"]
        qty = item["qty"]
        if product.stock_qty < qty:
            insufficient.append(item)
    return insufficient


@transaction.atomic
def _consume_inventory_batches(product_id: int, qty: int) -> None:
    """Remove `qty` units from the physical stock batches (oldest first)
    so the Inventory (ສາງສິນຄ້າ) list staff/admin see visibly drops."""
    from apps.inventory.models import Inventory

    remaining = qty
    batches = (
        Inventory.objects.filter(product_id=product_id, quantity__gt=0)
        .order_by("created_at")
    )
    for batch in batches:
        if remaining <= 0:
            break
        take = min(batch.quantity, remaining)
        Inventory.objects.filter(pk=batch.pk).update(quantity=F("quantity") - take)
        remaining -= take


@transaction.atomic
def deduct_stock(product_id: int, qty: int) -> None:
    """A sale is finally confirmed (staff approved a slip, POS sale, or a
    reservation completed that was never pre-allocated). Removes the sold
    units from both the available pool and the underlying batches.

    Clamped at 0 — stock_qty is a PositiveIntegerField (DB check
    constraint), and a reservation can be marked complete by staff even
    if it was never actually restocked in the system."""
    Product.objects.filter(pk=product_id).update(
        stock_qty=Greatest(F("stock_qty") - qty, 0)
    )
    _consume_inventory_batches(product_id, qty)


@transaction.atomic
def consume_allocated_stock(product_id: int, qty: int) -> None:
    """A reservation that was already earmarked (stock_ready=True) is now
    being picked up. The available-pool portion was already removed when
    it became stock_ready — only the physical batch needs updating now."""
    _consume_inventory_batches(product_id, qty)


@transaction.atomic
def release_stock(product_id: int, qty: int) -> None:
    """Reverse an earmark — used when a stock_ready reservation is
    cancelled, so the units become available again."""
    Product.objects.filter(pk=product_id).update(stock_qty=F("stock_qty") + qty)


@transaction.atomic
def receive_stock(product_id: int, qty: int) -> None:
    """Called when new stock physically arrives (an Inventory/ImportDetail
    record is created). Adds to the available pool, then earmarks it for
    the most recent pending reservations first."""
    from apps.sales.models import Reserved

    product = Product.objects.select_for_update().get(pk=product_id)
    product.stock_qty += qty
    product.save(update_fields=["stock_qty"])

    pending = Reserved.objects.filter(
        product_id=product_id, status=Reserved.Status.RESERVED, stock_ready=False,
    ).order_by("-res_date")

    for reservation in pending:
        if product.stock_qty <= 0:
            break
        if product.stock_qty >= reservation.quantity:
            product.stock_qty -= reservation.quantity
            reservation.stock_ready = True
            reservation.save(update_fields=["stock_ready"])

    product.save(update_fields=["stock_qty"])
