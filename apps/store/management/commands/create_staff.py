import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a staff user for /staff/ portal (not full superuser)"

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.getenv("STAFF_USER", "staff"))
        parser.add_argument("--password", default=os.getenv("STAFF_PASSWORD", "StaffMatcha2026!"))
        parser.add_argument("--email", default=os.getenv("STAFF_EMAIL", "staff@matchashop.com"))
        parser.add_argument("--name", default=os.getenv("STAFF_NAME", "ພະນັກງານ"))
        parser.add_argument("--reset", action="store_true", help="Reset password if user exists")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        password = options["password"]
        email = options["email"]
        name = (options["name"] or "").strip()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": name,
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
        )

        if not created:
            if not options["reset"]:
                self.stdout.write(f"User '{username}' already exists — use --reset to update password")
                return
            user.is_staff = True
            user.is_active = True
            user.email = email or user.email
            if name:
                user.first_name = name

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} staff user '{username}'"))
        self.stdout.write(f"  Login: /login/")
        self.stdout.write(f"  Username: {username}")
        self.stdout.write(f"  Password: {password}")
