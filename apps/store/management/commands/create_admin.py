import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create superuser from env vars (idempotent)"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("ADMIN_USER", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@matchashop.com")
        password = os.getenv("ADMIN_PASSWORD", "")

        if not password:
            self.stdout.write("ADMIN_PASSWORD not set — skipping")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Admin '{username}' already exists")
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
