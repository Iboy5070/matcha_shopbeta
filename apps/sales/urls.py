from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

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
