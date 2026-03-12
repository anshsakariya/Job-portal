from django import forms
from job.models import Register
from .models import JobListing

class Register(forms.ModelForm):
    class Meta:
        model = Register
        fields = ['username', 'email', 'phone', 'password']
        widgets = {
            'password': forms.PasswordInput(), 
        } 

class JobForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'salary', 'location']
        