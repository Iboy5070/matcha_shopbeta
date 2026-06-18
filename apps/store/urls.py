from django.urls import path
from . import views
from .google_auth import google_login_callback, google_login_start

urlpatterns = [
    path("", views.home, name="store_home"),
    path("about/", views.about, name="store_about"),
    path("contact/", views.contact, name="store_contact"),
    path("faq/", views.faq, name="store_faq"),
    path("privacy/", views.privacy, name="store_privacy"),
    path("returns/", views.returns, name="store_returns"),
    path("shop/", views.shop, name="store_shop"),
    path("product/<int:variant_id>/", views.product_detail, name="store_product_detail"),

    path("cart/", views.cart, name="store_cart"),
    path("cart/add/<int:variant_id>/", views.add_to_cart, name="store_add_to_cart"),
    path("cart/remove/<int:variant_id>/", views.remove_one, name="store_remove_one"),
    path("cart/clear/", views.clear_cart, name="store_clear_cart"),

    path("checkout/", views.checkout, name="store_checkout"),
    path("order/<str:order_no>/success/", views.order_success, name="store_order_success"),

    path("register/", views.register, name="store_register"),
    path("login/", views.customer_login, name="store_login"),
    path("logout/", views.customer_logout, name="store_logout"),
    path("account/", views.account, name="store_account"),
    path("auth/google/", google_login_start, name="store_google_login"),
    path("auth/google/callback/", google_login_callback, name="store_google_callback"),

    path("confirm-payment/", views.confirm_payment, name="store_confirm_payment"),
    path("blog/", views.blog_list, name="store_blog_list"),
]
