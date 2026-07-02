import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Membuat akun Admin default dari environment variable jika belum ada."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin12345")

        if User.objects.using("default").filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Admin '{username}' sudah ada. Dilewati."))
            return

        User.objects.db_manager("default").create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' berhasil dibuat."))
