import random
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.email

    @property
    def first_name_display(self):
        if self.full_name:
            parts = self.full_name.strip().split()
            if parts:
                return parts[0]
        if self.username:
            return self.username
        return self.email.split('@')[0]

    @property
    def second_name_display(self):
        if self.full_name:
            parts = self.full_name.strip().split()
            if len(parts) > 1:
                return parts[1]
            elif parts:
                return parts[0]
        if self.username:
            return self.username
        return self.email.split('@')[0]


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('compliment', 'Compliment'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default='other')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        display_name = self.name or "Anonymous"
        return f"{display_name} - {self.get_feedback_type_display()}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def message_preview(self):
        return self.message[:100] + '...' if len(self.message) > 100 else self.message


class EmailVerification(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def __str__(self):
        return f"{self.email} - {self.code}"
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit verification code"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def is_expired(self):
        """Check if code is older than 5 minutes"""
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiry_time
    
    @classmethod
    def check_rate_limit(cls, email):
        """
        Check if email has exceeded rate limit (3 codes per hour).
        Returns tuple: (is_allowed, wait_time_seconds)
        """
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_attempts = cls.objects.filter(
            email=email,
            created_at__gte=one_hour_ago
        ).count()
        
        if recent_attempts >= 3:
            # Find the oldest attempt in the last hour
            oldest_attempt = cls.objects.filter(
                email=email,
                created_at__gte=one_hour_ago
            ).order_by('created_at').first()
            
            if oldest_attempt:
                # Calculate when the rate limit will reset
                reset_time = oldest_attempt.created_at + timedelta(hours=1)
                wait_seconds = int((reset_time - timezone.now()).total_seconds())
                return False, max(wait_seconds, 0)
            
            return False, 3600  # Default to 1 hour wait
        
        return True, 0
    
    @classmethod
    def can_resend(cls, email):
        """
        Check if user can resend code (60 second cooldown).
        Returns tuple: (can_resend, wait_time_seconds)
        """
        last_code = cls.objects.filter(email=email).order_by('-created_at').first()
        
        if last_code:
            time_since_last = timezone.now() - last_code.created_at
            if time_since_last.total_seconds() < 60:
                wait_seconds = int(60 - time_since_last.total_seconds())
                return False, wait_seconds
        
        return True, 0
    
    @classmethod
    def create_verification(cls, email):
        """
        Create a new verification code for an email.
        Checks rate limiting before creating.
        """
        # Check rate limit
        is_allowed, wait_time = cls.check_rate_limit(email)
        if not is_allowed:
            minutes = wait_time // 60
            seconds = wait_time % 60
            raise ValueError(
                f"Too many attempts. Please try again in {minutes}m {seconds}s."
            )
        
        # Delete old unverified codes for this email
        cls.objects.filter(email=email, is_verified=False).delete()
        
        code = cls.generate_code()
        return cls.objects.create(email=email, code=code)
