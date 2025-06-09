from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task


class UserRegisterForm(UserCreationForm):
    email: forms.EmailField = forms.EmailField()

    class Meta:
        model = User
        fields: list[str] = ['username', 'email', 'password1', 'password2']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields: list[str] = [
            'title', 
            'description',
            'completed',
            'due_date',
            'priority'
            ]  
        widgets: dict[str, forms.DateTimeInput] = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()
