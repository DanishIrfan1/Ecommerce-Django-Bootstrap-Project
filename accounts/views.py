from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth

# Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode # this is used to encode the user id
from django.utils.encoding import force_bytes # this is used to encode the user id
from django.core.mail import EmailMessage # this is used to send the email
from django.contrib.auth.tokens import default_token_generator # this is used to encode the token


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name'] # cleaned_data is used to get the data from the form
            last_name = form.cleaned_data['last_name'] # cleaned_data is used to get the data from the form
            phone_number = form.cleaned_data['phone_number'] # cleaned_data is used to get the data from the form
            email = form.cleaned_data['email'] # cleaned_data is used to get the data from the form
            password = form.cleaned_data['password'] # cleaned_data is used to get the data from the form
            username = email.split('@')[0] # this is used to get the username from the email

            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password) # this is used to create a new user
            user.phone_number = phone_number # this is used to add the phone number to the user
            user.save() # this is used to save the user in the database

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # this is used to encode the user id
                'token': default_token_generator.make_token(user), # this is used to encode the token
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Registration Successful') # this is used to display a success message
            return redirect('register')

    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request,email=email,password=password)

        if user is not None:
            auth.login(request,user)
            # messages.success(request,'You are now logged in')
            return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login') # this is used to make sure that the user is logged in before they can access the logout
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')