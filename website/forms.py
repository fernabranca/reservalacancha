from django import forms
from django.forms import PasswordInput, TextInput, HiddenInput
from django.contrib.auth.models import User
from website.models import Cancha


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

class CanchaForm(forms.ModelForm): 
    class Meta: 
         model =  Cancha
         widgets = {
            'duenio': HiddenInput()
         }