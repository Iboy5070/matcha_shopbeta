from django.urls import path
from . import views, staff_views

urlpatterns = [
    # POS
    path('pos/', views.pos_view, name='pos'),
    path('pos/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('pos/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('pos/clear/', views.clear_cart, name='clear_cart'),
    path('pos/checkout/', views.pos_checkout, name='pos_checkout'),
    path('pos/reserve/', views.pos_reserve_form, name='pos_reserve_form'),
    path('pos/reserve/confirm/', views.pos_reserve_checkout, name='pos_reserve_checkout'),
    path('pos/collect/<int:order_id>/', views.pos_collect_balance, name='pos_collect_balance'),

    # Staff Dashboard
    path('staff/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('staff/login/', staff_views.staff_login, name='staff_login'),
    path('staff/logout/', staff_views.staff_logout, name='staff_logout'),
    path('staff/slips/', staff_views.staff_slips, name='staff_slips'),
    path('staff/slips/<int:order_id>/verify/', staff_views.verify_slip, name='verify_slip'),
    path('staff/orders/<int:order_id>/', staff_views.staff_order_detail, name='staff_order_detail'),
    path('staff/orders/<int:order_id>/print/deposit/', staff_views.staff_print_deposit, name='staff_print_deposit'),
    path('staff/orders/<int:order_id>/print/bill/', staff_views.staff_print_bill, name='staff_print_bill'),
    path('staff/reports/daily/', staff_views.staff_daily_report, name='staff_daily_report'),
    path('staff/reserved/', staff_views.staff_reserved, name='staff_reserved'),
    path('staff/reserved/order/<int:order_id>/action/', staff_views.staff_reserved_order_action, name='staff_reserved_order_action'),
    path('staff/reserved/<int:reserved_id>/action/', staff_views.staff_reserved_action, name='staff_reserved_action'),
    path('staff/inventory/', staff_views.staff_inventory, name='staff_inventory'),
    path('staff/inventory/po/<int:po_id>/print/', staff_views.staff_print_po, name='staff_print_po'),
    path('staff/inventory/import/<int:import_id>/print/', staff_views.staff_print_import, name='staff_print_import'),
]
