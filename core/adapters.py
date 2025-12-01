from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Customize social account signup to populate our CustomUser fields.
    """
    
    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get full name from Google (multiple possible field names)
        full_name = None
        if 'name' in data:
            full_name = data['name']
        elif 'given_name' in data:
            given = data.get('given_name', '')
            family = data.get('family_name', '')
            full_name = f"{given} {family}".strip()
        elif 'first_name' in data and 'last_name' in data:
            full_name = f"{data['first_name']} {data['last_name']}".strip()
        
        if full_name:
            user.full_name = full_name
        
        # Set email
        if 'email' in data:
            user_email(user, data['email'])
        
        # Generate unique username from email
        if user.email:
            base_username = user.email.split('@')[0]
            username = base_username
            
            # Handle duplicate usernames
            from core.models import CustomUser
            counter = 1
            while CustomUser.objects.filter(username=username).exclude(pk=user.pk).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Connect social account to existing user if email matches.
        """
        # If user is already logged in, connect the account
        if request.user.is_authenticated:
            return
        
        # Check if user with this email already exists
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                from core.models import CustomUser
                existing_user = CustomUser.objects.get(email=email)
                # Connect the social account to existing user
                sociallogin.connect(request, existing_user)
        except CustomUser.DoesNotExist:
            pass