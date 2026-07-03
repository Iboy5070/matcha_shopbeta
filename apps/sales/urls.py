from django.urls import path
from . import views
from .staff_views import staff_dashboard, staff_login, staff_logout
from .staff_manage_views import staff_products, staff_slips, staff_web_order_detail, staff_web_orders

urlpatterns = [
    path("staff/login/", staff_login, name="staff_login"),
    path("staff/logout/", staff_logout, name="staff_logout"),
    path("staff/", staff_dashboard, name="staff_dashboard"),
    path("staff/web-orders/", staff_web_orders, name="staff_web_orders"),
    path("staff/web-orders/<str:order_no>/", staff_web_order_detail, name="staff_web_order_detail"),
    path("staff/slips/", staff_slips, name="staff_slips"),
    path("staff/products/", staff_products, name="staff_products"),
    path("pos/", views.pos, name="pos"),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),
    path("pos/receipt/<int:order_id>/", views.pos_receipt, name="pos_receipt"),

    path("add/<int:variant_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:variant_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("orders/", views.orders_list, name="orders_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("refund/<int:order_id>/", views.refund_order, name="refund_order"),

]
