from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name='store_home'),
    path('shop/', views.store_shop, name='store_shop'),
    path('product/<int:product_id>/', views.store_product_detail, name='store_product_detail'),
    path('cart/', views.store_cart, name='store_cart'),
    path('cart/add/<int:product_id>/', views.store_add_to_cart, name='store_add_to_cart'),
    path('cart/remove/<int:product_id>/', views.store_remove_one, name='store_remove_one'),
    path('cart/clear/', views.store_clear_cart, name='store_clear_cart'),
    path('checkout/', views.store_checkout, name='store_checkout'),
    path('order/<int:order_id>/pay/', views.store_confirm_payment, name='store_confirm_payment'),
    
    path('login/', views.store_login, name='store_login'),
    path('register/', views.store_register, name='store_register'),
    path('logout/', views.store_logout, name='store_logout'),
    path('contact/', views.store_contact, name='store_contact'),
    path('about/', views.store_about, name='store_about'),
    path('blog/', views.store_blog_list, name='store_blog_list'),
    path('faq/', views.store_faq, name='store_faq'),
    path('returns/', views.store_returns, name='store_returns'),
    path('privacy/', views.store_privacy, name='store_privacy'),
    path('google-login/', views.store_google_login, name='store_google_login'),
]
