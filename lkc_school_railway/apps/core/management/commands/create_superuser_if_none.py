from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create a superuser if none exists (for Railway deployment)'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'lkc-admin-2026')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@lkc.ac.bw')
            User.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created'))
        else:
            self.stdout.write('Superuser already exists, skipping')
