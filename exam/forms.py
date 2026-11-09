from django import forms
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label = "Username",
        max_length=50, 
        validators=[MinLengthValidator(5)]
    )
    password1 = forms.CharField(
        label = "Password",
        widget=forms.PasswordInput(),
        validators=[MinLengthValidator(8)]
    )
    password2 = forms.CharField(
        label = "Confirm password",
        widget=forms.PasswordInput(),
        validators=[MinLengthValidator(8)]
    )
