from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomerSetPasswordForm

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
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='store/password_reset.html',
            email_template_name='store/password_reset_email.txt',
            subject_template_name='store/password_reset_subject.txt',
            success_url=reverse_lazy('store_password_reset_done'),
        ),
        name='store_password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='store/password_reset_done.html',
        ),
        name='store_password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='store/password_reset_confirm.html',
            form_class=CustomerSetPasswordForm,
            success_url=reverse_lazy('store_password_reset_complete'),
        ),
        name='store_password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='store/password_reset_complete.html',
        ),
        name='store_password_reset_complete',
    ),
    path('account/', views.store_account, name='store_account'),
    path('account/orders/', views.store_account_orders, name='store_account_orders'),
    path('account/edit/', views.store_account_edit, name='store_account_edit'),
    path('contact/', views.store_contact, name='store_contact'),
    path('about/', views.store_about, name='store_about'),
    path('blog/', views.store_blog_list, name='store_blog_list'),
    path('faq/', views.store_faq, name='store_faq'),
    path('returns/', views.store_returns, name='store_returns'),
    path('privacy/', views.store_privacy, name='store_privacy'),
    path('google-login/', views.store_google_login, name='store_google_login'),
]
