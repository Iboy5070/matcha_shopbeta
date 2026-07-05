import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Try to get or create admin user
user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
user.set_password('admin')
user.is_staff = True
user.is_superuser = True
user.save()
print("Superuser 'admin' with password 'admin' created/updated successfully!")
