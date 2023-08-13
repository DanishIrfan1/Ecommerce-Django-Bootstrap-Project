from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm): # because we are using model forms we need to import the model
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control',
    }))

    class Meta: # this is the meta class that will be used to specify the model and the fields that we want to use
        model = Account # this is the model that we want to use
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password'] # these are the fields that we want to use

    def __init__(self,*args,**kwargs): # this is the init method that will be used to add placeholders and classes to the fields
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self): # this is the clean method that will be used to check if the password and the confirm password are the same
        cleaned_data = super(RegistrationForm, self).clean() # this line means that we are getting the data from the form
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )