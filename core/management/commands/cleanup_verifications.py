from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import EmailVerification


class Command(BaseCommand):
    help = 'Delete expired email verification codes older than 24 hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Delete verifications older than this many hours (default: 24)'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Delete old verifications
        deleted_count, _ = EmailVerification.objects.filter(
            created_at__lt=cutoff_time
        ).delete()
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} expired verification(s) older than {hours} hours.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'No expired verifications found older than {hours} hours.'
                )
            )