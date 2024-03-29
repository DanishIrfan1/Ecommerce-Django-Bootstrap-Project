import requests
from django.shortcuts import HttpResponse, get_object_or_404

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth

# Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # this is used to encode the user id
from django.utils.encoding import force_bytes  # this is used to encode the user id
from django.core.mail import EmailMessage  # this is used to send the email
from django.contrib.auth.tokens import default_token_generator  # this is used to encode the token


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']  # cleaned_data is used to get the data from the form
            last_name = form.cleaned_data['last_name']  # cleaned_data is used to get the data from the form
            phone_number = form.cleaned_data['phone_number']  # cleaned_data is used to get the data from the form
            email = form.cleaned_data['email']  # cleaned_data is used to get the data from the form
            password = form.cleaned_data['password']  # cleaned_data is used to get the data from the form
            username = email.split('@')[0]  # this is used to get the username from the email

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username,
                                               password=password)  # this is used to create a new user
            user.phone_number = phone_number  # this is used to add the phone number to the user
            user.save()  # this is used to save the user in the database

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # this is used to encode the user id
                'token': default_token_generator.make_token(user),  # this is used to encode the token
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request,'Thankyou for registration with us. We have sent a verification email to your email address. Please verify it.') # this is used to display a success message
            return redirect(
                '/accounts/login/?command=verification&email=' + email)  # this is used to redirect the user to the login page

    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            try:  # this is used to check if the user has a cart_item in the cart when he is not logged in and clicks on the login button
                cart = Cart.objects.get(
                    cart_id=_cart_id(request))  # get the cart using the _cart_id present in the session
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()  # check if the cart_item already exists or not
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)  # get the cart_item using the cart
                    # Getting the product variations by cart id
                    # this below code written because to grouping the cart_item by the product variation after the user is logged in
                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()  # get all the variation of the cart_item
                        product_variation.append(list(variation))  # append the variation in the product_variation

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)  # get the cart_item using the user
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()  # get all the variation of the cart_item
                        existing_variation_list.append(
                            list(existing_variation))  # append the variation in the existing_variation_list
                        id.append(item.id)  # append the id in the id list

                    # product_variation[1,2,3,4,6] -> database
                    # existing_variation_list[3,4,7] -> product_variation list
                    # now getting common variation from the above two list and increase the quantity of the cart_item
                    # id -> database

                    for pr in product_variation:  # iterate over the product_variation
                        if pr in existing_variation_list:  # if the product_variation is in the existing_variation_list
                            index = existing_variation_list.index(pr)  # get the index of the existing_variation_list
                            item_id = id[index]  # get the id using the index
                            item = CartItem.objects.get(id=item_id)  # get the cart_item using the id
                            item.quantity += 1  # increase the quantity by 1
                            item.user = user  # set the user
                            item.save()  # save the cart_item
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)  # get the cart_item using the cart
                            for item in cart_item:  # iterate over the cart_item
                                item.user = user  # set the user
                                item.save()  # save the cart_item
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            url = request.META.get('HTTP_REFERER')  # this is used to get the previous url
            try:
                query = requests.utils.urlparse(url).query  # this is used to get the query string from the url
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split(
                    '&'))  # this is used to convert the query string to dictionary, split the query string by & and then split the key and value by =
                if 'next' in params:  # this is used to check if the next is present in the params
                    nextPage = params['next']  # this is used to get the next page
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(
    login_url='login')  # this is used to make sure that the user is logged in before they can access the logout
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(
            uidb64).decode()  # this is used to decode the user id, it give primary key of the user which is encoded in the url
        user = Account._default_manager.get(pk=uid)  # this is used to get the user
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,
                                                                token):  # this is used to check if the user exists and if the token is valid with that user
        user.is_active = True  # this is used to activate the user
        user.save()  # this is used to save the user
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(
    login_url='login')  # this is used to make sure that the user is logged in before they can access the dashboard
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,
                                                          is_ordered=True)  # this is used to get the orders of the user
    orders_count = orders.count()  # this is used to get the count of the orders

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,

    }
    return render(request, 'accounts/dashboard.html', context)


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():  # this is used to check if the email exists in the database
            user = Account.objects.get(
                email__exact=email)  # this is used to get the user, __exact is used to get the exact email and case sensitive

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # this is used to encode the user id
                'token': default_token_generator.make_token(user),  # this is used to encode the token
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')
        else:  # this is used to display an error message if the email does not exist in the database
            messages.error(request, 'Account does not exist')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(
            uidb64).decode()  # this is used to decode the user id, it give primary key of the user which is encoded in the url
        user = Account._default_manager.get(pk=uid)  # this is used to get the user
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,
                                                                token):  # this is used to check if the user exists and if the token is valid with that user
        request.session['uid'] = uid  # this is used to store the user id in the session
        messages.success(request, 'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')


def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:  # this is used to check if the password and confirm password are the same
            uid = request.session.get('uid')  # this is used to get the user id from the session
            user = Account.objects.get(pk=uid)  # this is used to get the user
            user.set_password(
                password)  # this is used to set the password, by using set_password it will automatically hash the password
            user.save()  # this is used to save the user
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered = True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user) # this is used to get the userprofile of the current user
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user) # instance=request.user is used to get the current user and just update the user
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile) # instance=userprofile is used to get the current userprofile and just update the userprofile
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated')
            return redirect('edit_profile')
    else: # this is used to display the current user information in the form, if the request is not post
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }

    return render(request, 'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username) # this is used to get the current user
        if new_password == confirm_password: # this is used to check if the new password and confirm password are the same
            success = user.check_password(current_password) # check_password is built in method in Django to check the password, it will return true if the password is correct, also it will automatically hash the password
            if success: # this is used to check if the password is correct
                user.set_password(new_password) # set_password is used to set the password, by using set_password it will automatically hash the password, it will also log out the user, it is a built in method in Django
                user.save() # this is used to save the user
                # auth.logout(request) # this is used to log out the user
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request,'Please enter correct current password')
                return redirect('change_password')
        else:
            messages.error(request,'Passwords do not match')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id) # this is used to get the order detail of the order, order__order_number is used to get the order using the order number, __ is refering to the foreign key
    order = Order.objects.get(order_number=order_id) # this is used to get the order using the order number
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }

    return render(request, 'accounts/order_detail.html',context)