import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create superuser from env vars (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset password and permissions when the user already exists",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("ADMIN_USER", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@matchashop.com")
        password = os.getenv("ADMIN_PASSWORD", "")

        if not password:
            self.stdout.write("ADMIN_PASSWORD not set — skipping")
            return

        user = User.objects.filter(username=username).first()
        if user:
            if not options["reset"]:
                self.stdout.write(f"Admin '{username}' already exists")
                return
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin '{username}' reset"))
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
