from django import forms
from barberian.auth.models import User
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

class StaffCreationForm(forms.ModelForm):
    """Form for creating new staff members"""
    password = forms.CharField(widget=forms.PasswordInput(), validators=[validate_password])
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'staff'
        if commit:
            user.save()
        return user
