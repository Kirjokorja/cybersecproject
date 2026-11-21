from django import forms
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth import get_user_model
from .models import User

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}

    username = forms.CharField(
        label = "Username",
        max_length=30, 
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
