from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email Address', 'id': 'id_reg_email'
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'First Name', 'id': 'id_first_name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Last Name', 'id': 'id_last_name'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Username', 'id': 'id_username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Password', 'id': 'id_password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Confirm Password', 'id': 'id_password2'
        })


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username', 'id': 'id_login_username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password', 'id': 'id_login_password'
    }))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input', 'id': 'id_profile_first_name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'id': 'id_profile_last_name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'id': 'id_profile_email'
    }))

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_profile_phone'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_profile_address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_profile_city'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_profile_state'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_profile_zip'}),
        }
