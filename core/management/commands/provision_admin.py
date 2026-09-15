import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the deployment admin from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME")
        email = os.environ.get("DJANGO_ADMIN_EMAIL")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not any((username, email, password)):
            self.stdout.write("Admin provisioning skipped: admin variables are not configured.")
            return
        if not all((username, email, password)):
            raise CommandError(
                "Set DJANGO_ADMIN_USERNAME, DJANGO_ADMIN_EMAIL, and DJANGO_ADMIN_PASSWORD together."
            )

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Deployment admin {action}: {username}"))
