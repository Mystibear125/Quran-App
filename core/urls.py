from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    signin, signup_step1_email, signup_step2_verify, signup_step2_resend,
    signup_step3_complete, home, feedback, contactus, aboutus, 
    logout_view, surah_audio
)

urlpatterns = [
    # Main pages
    path('', home, name='home'),
    path('feedback/', feedback, name='feedback'),
    path('contactus/', contactus, name='contactus'),
    path('aboutus/', aboutus, name='aboutus'),
    
    # Auth - 3-Step Signup
    path('signup/', signup_step1_email, name='signup_step1_email'),
    path('signup/verify/', signup_step2_verify, name='signup_step2_verify'),
    path('signup/resend/', signup_step2_resend, name='signup_step2_resend'),
    path('signup/complete/', signup_step3_complete, name='signup_step3_complete'),
    path('signin/', signin, name='signin'),
    path('logout/', logout_view, name='logout'),
    
    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset/password_reset_form.html',
             email_template_name='password_reset/password_reset_email.html',
             subject_template_name='password_reset/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Surah audio
    path('surah/audio/<int:surah_number>/', surah_audio, name='surah_audio'),
]