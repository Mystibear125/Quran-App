from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if any superuser exists
        if not User.objects.filter(is_superuser=True).exists():
            # Create superuser with environment variables
            import os
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@alquran.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            
            User.objects.create_superuser(
                email=email,
                password=password,
                full_name='Admin',
                username='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))