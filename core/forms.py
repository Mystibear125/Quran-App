from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser, Feedback, ContactMessage, EmailVerification



# ==================== STEP 1: Email Entry ====================
class EmailEntryForm(forms.Form):
    """Step 1: User enters their email"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


# ==================== STEP 2: Code Verification ====================
class CodeVerificationForm(forms.Form):
    """Step 2: User enters 6-digit code"""
    code = forms.CharField(
        label="Verification Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'autofocus': True,
            'style': 'text-align: center; letter-spacing: 0.5rem; font-size: 1.5rem;'
        })
    )
    
    def __init__(self, email=None, *args, **kwargs):
        self.email = email
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        
        if not self.email:
            raise forms.ValidationError("Session expired. Please start again.")
        
        try:
            verification = EmailVerification.objects.filter(
                email=self.email,
                code=code,
                is_verified=False
            ).latest('created_at')
            
            if verification.is_expired():
                raise forms.ValidationError("This code has expired. Please request a new one.")
            
            # Mark as verified
            verification.is_verified = True
            verification.save()
            
            return code
            
        except EmailVerification.DoesNotExist:
            raise forms.ValidationError("Invalid verification code.")


# ==================== STEP 3: Complete Registration ====================
class CompleteRegistrationForm(UserCreationForm):
    """Step 3: User completes registration with name and password"""
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'autofocus': True
        })
    )

    class Meta:
        model = CustomUser
        fields = ["full_name", "password1", "password2"]
    
    def __init__(self, email=None, *args, **kwargs):
        self.email = email
        super().__init__(*args, **kwargs)
        
        # Customize password field placeholders
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.email
        user.username = self.email.split('@')[0]  # Auto-generate username from email
        user.full_name = self.cleaned_data['full_name']
        
        if commit:
            user.save()
        return user


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)

    class Meta:
        model = CustomUser
        fields = ["full_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    

class SignInForm(forms.Form):
    """
    Form for user sign in with email and password.
    """
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'autofocus': True})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "The email or password you entered is incorrect.",
                    code='invalid_login',
                )
        
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class FeedbackForm(forms.ModelForm):
    """
    Form for user feedback submissions.
    """
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'feedback_type', 'rating', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Anonymous'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
            'feedback_type': forms.Select(attrs={'required': True}),
            'rating': forms.RadioSelect(
                choices=[(str(i), str(i)) for i in range(5, 0, -1)]
            ),
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Tell us what you think...'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating in [None, '']:
            return None
        return int(rating)


class ContactForm(forms.ModelForm):
    """
    Form for contact us page submissions.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': "What's this about?",
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write your message here...',
                'required': True
            }),
        }