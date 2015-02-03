from django import forms
from django.forms import PasswordInput, TextInput
from django.contrib.auth.models import User


class UserForm(forms.ModelForm): 
    class Meta: 
         model =  User
         fields = (
         	'username', 
         	'first_name', 
         	'last_name',
         	'email',
         	'password')
         widgets = {
            'password': PasswordInput()
        	} 
