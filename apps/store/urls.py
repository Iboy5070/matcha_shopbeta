from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="store_home"),
    path("shop/", views.shop, name="store_shop"),
    path("product/<int:variant_id>/", views.product_detail, name="store_product_detail"),

    path("cart/", views.cart, name="store_cart"),
    path("cart/add/<int:variant_id>/", views.add_to_cart, name="store_add_to_cart"),
    path("cart/remove/<int:variant_id>/", views.remove_one, name="store_remove_one"),
    path("cart/clear/", views.clear_cart, name="store_clear_cart"),

    path("checkout/", views.checkout, name="store_checkout"),
    path("order/<str:order_no>/success/", views.order_success, name="store_order_success"),

    path("confirm-payment/", views.confirm_payment, name="store_confirm_payment"),
        # ✅ ADD THESE
    path("blog/", views.blog_list, name="store_blog_list"),
    path("faq/", views.faq, name="store_faq"),
    path("contact/", views.contact, name="store_contact"),
]
