#encoding:utf-8
from django import forms
from django.forms import PasswordInput, TextInput, HiddenInput
from django.contrib.auth.models import User
from website.models import Cancha, Complejo


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

    def save(self, commit=True):
        
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'La dirección de correo ya existe. La misma debe ser única')
        return email

class CanchaForm(forms.ModelForm): 
    class Meta: 
         model =  Cancha
         widgets = {
            'numero_cancha': HiddenInput()
         }

class ComplejoForm(forms.ModelForm):
    class Meta:
        model = Complejo
        widgets = {
            'direccion': HiddenInput(),
            'latitud': HiddenInput(),
            'longitud': HiddenInput(),
            'duenio': HiddenInput()
         }