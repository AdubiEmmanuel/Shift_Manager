from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=32)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    line_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.ROLE_LINE_MANAGER), required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "line_manager",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=32)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "line_manager")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if email and qs.exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
