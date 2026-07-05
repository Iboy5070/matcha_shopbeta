from django.urls import path
from . import views, staff_views

urlpatterns = [
    # POS
    path('pos/', views.pos_view, name='pos'),
    path('pos/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('pos/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('pos/clear/', views.clear_cart, name='clear_cart'),
    path('pos/checkout/', views.pos_checkout, name='pos_checkout'),
    
    # Staff Dashboard
    path('staff/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('staff/login/', staff_views.staff_login, name='staff_login'),
    path('staff/logout/', staff_views.staff_logout, name='staff_logout'),
    path('staff/slips/', staff_views.staff_slips, name='staff_slips'),
    path('staff/slips/<int:order_id>/verify/', staff_views.verify_slip, name='verify_slip'),
]
