# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Enter your password',
        })
    )

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled widget."""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Enter your email',
            'autofocus': True,
        })
    )

    def clean_email(self):
        """Validate that email exists in the system."""
        email = self.cleaned_data.get('email')
        if email and not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email

class CustomSetPasswordForm(SetPasswordForm):
    """Custom password set form with styled widgets."""
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Enter new password',
            'autofocus': True,
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Confirm new password',
        })
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Enter your email',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'sp-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'sp-input',
            'placeholder': 'Last name',
        })
    )

    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please log in or use a different email.')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'sp-input'}),
            'email': forms.EmailInput(attrs={'class': 'sp-input'}),
            'first_name': forms.TextInput(attrs={'class': 'sp-input'}),
            'last_name': forms.TextInput(attrs={'class': 'sp-input'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'sp-input'}),
            'last_name': forms.TextInput(attrs={'class': 'sp-input'}),
            'email': forms.EmailInput(attrs={'class': 'sp-input'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # We added date_of_birth, language, promo_emails, and sms_alerts to this list!
        fields = ['gender', 'phone_number', 'country', 'profile_picture', 'date_of_birth', 'language', 'promo_emails', 'sms_alerts']
        widgets = {
            'gender': forms.Select(attrs={'class': 'sp-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'sp-input'}),
            'country': forms.TextInput(attrs={'class': 'sp-input'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            
            # The 'type': 'date' attribute forces the browser to show a calendar popup!
            'date_of_birth': forms.DateInput(attrs={'class': 'sp-input', 'type': 'date'}),
            'language': forms.TextInput(attrs={'class': 'sp-input'}),
            
            # Simple checkboxes for the notifications
            'promo_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }