from django.shortcuts import HttpResponse

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
            # messages.success(request,'Thankyou for registration with us. We have sent a verification email to your email address. Please verify it.') # this is used to display a success message
            return redirect('/accounts/login/?command=verification&email='+email) # this is used to redirect the user to the login page

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
            messages.success(request,'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login') # this is used to make sure that the user is logged in before they can access the logout
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # this is used to decode the user id, it give primary key of the user which is encoded in the url
        user = Account._default_manager.get(pk=uid) # this is used to get the user
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token): # this is used to check if the user exists and if the token is valid with that user
        user.is_active = True # this is used to activate the user
        user.save() # this is used to save the user
        messages.success(request,'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url='login') # this is used to make sure that the user is logged in before they can access the dashboard
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists(): # this is used to check if the email exists in the database
            user = Account.objects.get(email__exact=email) # this is used to get the user, __exact is used to get the exact email and case sensitive

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # this is used to encode the user id
                'token': default_token_generator.make_token(user), # this is used to encode the token
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')
        else: # this is used to display an error message if the email does not exist in the database
            messages.error(request,'Account does not exist')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')


def resetpassword_validate (request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # this is used to decode the user id, it give primary key of the user which is encoded in the url
        user = Account._default_manager.get(pk=uid) # this is used to get the user
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token): # this is used to check if the user exists and if the token is valid with that user
        request.session['uid'] = uid # this is used to store the user id in the session
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired')
        return redirect('login')


def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password: # this is used to check if the password and confirm password are the same
            uid = request.session.get('uid') # this is used to get the user id from the session
            user = Account.objects.get(pk=uid) # this is used to get the user
            user.set_password(password) # this is used to set the password, by using set_password it will automatically hash the password
            user.save() # this is used to save the user
            messages.success(request,'Password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Passwords do not match')
            return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')