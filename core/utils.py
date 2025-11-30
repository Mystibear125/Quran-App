from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(email, code):
    """Send verification code to user's email with HTML template"""
    subject = 'Verify Your Email - Al-Qur\'an'
    
    # Render HTML email
    html_message = render_to_string('emails/verification_email.html', {
        'code': code,
    })
    
    # Create plain text version (fallback)
    plain_message = f'''
Assalamu Alaikum,

Your verification code is: {code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

Best regards,
The Al-Qur'an Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@alquran.com'
    
    try:
        # Create email with both HTML and plain text
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[email]
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False