import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

tables = [
    'store_weborderitem', 'store_paymentconfirmation', 'store_weborder', 'store_customerprofile',
    'sales_payment', 'sales_reserved', 'sales_bill', 'sales_orderitem', 'sales_order', 'sales_customer',
    'inventory_stockmovement', 
    'catalog_productvariant', 'catalog_product', 'catalog_category',
    'cms_testimonial', 'cms_faqitem', 'cms_contactmessage'
]

with connection.cursor() as cursor:
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"Dropped {table}")
        except Exception as e:
            pass
            
    # Also delete migration history for these apps to force recreation
    cursor.execute("DELETE FROM django_migrations WHERE app IN ('sales', 'store', 'catalog', 'inventory', 'cms');")
    print("Cleared migration history for apps.")
