from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .forms import (
    SignInForm, EmailEntryForm, CodeVerificationForm, 
    CompleteRegistrationForm, FeedbackForm, ContactForm
)
from .models import EmailVerification
from .utils import send_verification_email


# ==================== AUTH VIEWS ====================

def signup_step1_email(request):
    """Step 1: User enters email"""
    if request.method == 'POST':
        form = EmailEntryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Create verification code (includes rate limit check)
                verification = EmailVerification.create_verification(email)
                
                # Send email
                if send_verification_email(email, verification.code):
                    # Store email in session
                    request.session['signup_email'] = email
                    messages.success(request, f"Verification code sent to {email}")
                    return redirect('signup_step2_verify')
                else:
                    messages.error(request, "Failed to send verification email. Please try again.")
            
            except ValueError as e:
                # Rate limit exceeded
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmailEntryForm()
    
    return render(request, 'signup/signup_step1.html', {'form': form})


def signup_step2_verify(request):
    """Step 2: User enters verification code"""
    email = request.session.get('signup_email')
    
    if not email:
        messages.error(request, "Session expired. Please start again.")
        return redirect('signup_step1_email')
    
    if request.method == 'POST':
        form = CodeVerificationForm(email=email, data=request.POST)
        if form.is_valid():
            # Code verified successfully - redirect to step 3
            return redirect('signup_step3_complete')
        # If form is invalid, errors will be shown below
    else:
        form = CodeVerificationForm(email=email)
    
    return render(request, 'signup/signup_step2.html', {
        'form': form,
        'email': email
    })


def signup_step2_resend(request):
    """Resend verification code with cooldown"""
    email = request.session.get('signup_email')
    
    if not email:
        messages.error(request, "Session expired. Please start again.")
        return redirect('signup_step1_email')
    
    # Check if user can resend (60 second cooldown)
    can_resend, wait_time = EmailVerification.can_resend(email)
    
    if not can_resend:
        messages.error(request, f"Please wait {wait_time} seconds before requesting a new code.")
        return redirect('signup_step2_verify')
    
    try:
        # Create new verification code
        verification = EmailVerification.create_verification(email)
        
        if send_verification_email(email, verification.code):
            messages.success(request, "New verification code sent! Check your email.")
        else:
            messages.error(request, "Failed to send email. Please try again.")
    
    except ValueError as e:
        # Rate limit exceeded
        messages.error(request, str(e))
    
    return redirect('signup_step2_verify')


def signup_step3_complete(request):
    """Step 3: User completes registration"""
    email = request.session.get('signup_email')
    
    if not email:
        messages.error(request, "Session expired. Please start again.")
        return redirect('signup_step1_email')
    
    # Verify that email was actually verified
    if not EmailVerification.objects.filter(email=email, is_verified=True).exists():
        messages.error(request, "Please verify your email first.")
        return redirect('signup_step2_verify')
    
    if request.method == 'POST':
        form = CompleteRegistrationForm(email=email, data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Clean up session
            del request.session['signup_email']
            
            messages.success(request, "Account created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompleteRegistrationForm(email=email)
    
    return render(request, 'signup/signup_step3.html', {
        'form': form,
        'email': email
    })


def signin(request):
    form = SignInForm(request, data=request.POST) if request.method == 'POST' else SignInForm()
    
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        
        first_name = (user.full_name.split()[1] if len(user.full_name.split()) > 1 else user.full_name) if user.full_name else user.username
        messages.success(request, f"Welcome back, {first_name}!")
        return redirect('home')
    elif request.method == 'POST':
        messages.error(request, "Please check your credentials and try again.")

    return render(request, 'signin/signin.html', {'form': form})


@login_required 
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# ==================== PAGE VIEWS (keep as is) ====================

def home(request):
    return render(request, 'home/index.html')


def feedback(request):
    """Handle feedback form submissions"""
    initial = {}
    if request.user.is_authenticated:
        initial = {
            'name': request.user.full_name or request.user.first_name_display,
            'email': request.user.email,
        }
    
    form = FeedbackForm(request.POST, initial=initial) if request.method == 'POST' else FeedbackForm(initial=initial)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Thank you! Your feedback has been recorded.")
        return redirect('feedback')
    elif request.method == 'POST':
        messages.error(request, "Please correct the errors below.")
    
    return render(request, 'feedback/feedback.html', {
        'form': form,
        'rating_options': [5, 4, 3, 2, 1]
    })


def contactus(request):
    """Handle contact form submissions"""
    initial = {}
    if request.user.is_authenticated:
        initial = {
            'name': request.user.full_name or request.user.first_name_display,
            'email': request.user.email,
        }
    
    form = ContactForm(request.POST) if request.method == 'POST' else ContactForm(initial=initial)
    
    if request.method == 'POST' and form.is_valid():
        contact_message = form.save(commit=False)
        
        # Auto-fill user data if logged in and fields empty
        if request.user.is_authenticated:
            contact_message.name = contact_message.name or request.user.full_name or request.user.first_name_display
            contact_message.email = contact_message.email or request.user.email
        
        contact_message.save()
        messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
        return redirect('contactus')
    elif request.method == 'POST':
        messages.error(request, "Please correct the errors below.")
    
    return render(request, 'contactus/contactus.html', {'form': form})


def aboutus(request):
    return render(request, 'aboutus/aboutus.html')


def surah_audio(request, surah_number):
    """Handle surah audio playback with validation"""
    if not (1 <= surah_number <= 114):
        messages.error(request, "Invalid Surah number.")
        return redirect('home')
    
    return render(request, 'home/surah_audio.html', {'surah_number': surah_number})