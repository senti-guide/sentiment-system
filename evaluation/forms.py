from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class StudentRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean_password_confirmation(self):
        # Check if the password and password_confirmation match
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise ValidationError("Passwords do not match.")
        return password_confirmation

    def save(self, commit=True):
        # Save the user with the password set correctly
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as the username
        user.set_password(self.cleaned_data['password'])  # Set the password
        if commit:
            user.save()
        return user
