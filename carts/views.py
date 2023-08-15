from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem


# Create your views here.

def _cart_id(request):  # _cart_id() is used to get the cart_id from the session
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id): # add_cart() is used to add the cart_item to the cart
    current_user = request.user  # get the current user
    product = Product.objects.get(id=product_id)  # get the product
    # if the user is authenticated, then get the user, else get the cart using the cart_id present in the session
    if current_user.is_authenticated:
        product_variation = []  # product_variation is used to store the variation of the product
        if request.method == 'POST':
            for item in request.POST:  # iterate over the request.POST, because the request.POST contains the product_id and the variation_id, multiple variation_id can be present
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        # get the variation using the product_id, key and value present in the request.POST
                        product=product_id,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    product_variation.append(variation)  # append the variation in the product_variation
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product,
                                                      user=current_user).exists() # check if the cart_item already exists or not of a particular user
        if is_cart_item_exists:  # if the cart_item already exists, then increase the quantity by 1
            # Create the cart item, if the cart item already exists, then increase the quantity also works for the product with variation
            cart_item = CartItem.objects.filter(product=product,
                                                user=current_user)  # get the cart_item using the product and user

            ex_var_list = []  # ex_var_list is used to store the variation of the cart_item
            id = []  # id is used to store the id of the cart_item
            for item in cart_item:  # iterate over the cart_item
                existing_variation = item.variation.all()  # get all the variation of the cart_item
                ex_var_list.append(list(existing_variation))  # append the variation in the ex_var_list
                id.append(item.id)  # append the id in the id list

            if product_variation in ex_var_list:  # if the product_variation is in the ex_var_list, then increase the quantity by 1
                # increase the cart_item quantity by 1
                index = ex_var_list.index(product_variation)  # get the index of the product_variation
                item_id = id[index]  # get the id of the cart_item using the index
                item = CartItem.objects.get(product=product, id=item_id)  # get the cart_item using the product and id
                item.quantity += 1  # increase the quantity by 1
                item.save()  # save the cart_item
            else:  # if the product_variation is not in the ex_var_list, then create the cart_item
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user,
                )
                if len(product_variation) > 0:  # if the product_variation is greater than 0, then the product has variation
                    item.variation.clear()  # clear the cart_item variation
                    item.variation.add(
                        *product_variation)  # add the variation in the cart_item, * mark is used to iterate over the product_variation
                # cart_item.quantity += 1  # if the cart_item already exists, then increase the quantity by 1
                item.save()
        else:  # if the cart_item does not exist, then create the cart_item
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )  # create the cart_item
            if len(product_variation) > 0:  # if the product_variation is greater than 0, then the product has variation
                cart_item.variation.clear()  # clear the cart_item variation
                cart_item.variation.add(
                    *product_variation)  # add the variation in the cart_item, * mark is used to iterate over the product_variation
            cart_item.save()
        return redirect('cart')
    # if the user is not authenticated, then get the cart using the cart_id present in the session
    else:
        product_variation = []  # product_variation is used to store the variation of the product
        if request.method == 'POST':
            for item in request.POST: # iterate over the request.POST, because the request.POST contains the product_id and the variation_id, multiple variation_id can be present
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get( # get the variation using the product_id, key and value present in the request.POST
                        product=product_id,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                    )
                    product_variation.append(variation) # append the variation in the product_variation
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the _cart_id present in the session
            # print("cart already exists")
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            # print("cart created")
        cart.save()  # save the cart in the session
        # print

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()  # check if the cart_item already exists or not
        if is_cart_item_exists:  # if the cart_item already exists, then increase the quantity by 1
            # Create the cart item, if the cart item already exists, then increase the quantity also works for the product with variation
            cart_item = CartItem.objects.filter(product=product,cart=cart)  # get the cart_item using the product and cart
            # existing_variation -> database
            # current_variation -> product_variation list
            # item_id -> database

            ex_var_list = []  # ex_var_list is used to store the variation of the cart_item
            id = []  # id is used to store the id of the cart_item
            for item in cart_item: # iterate over the cart_item
                existing_variation = item.variation.all() # get all the variation of the cart_item
                ex_var_list.append(list(existing_variation)) # append the variation in the ex_var_list
                id.append(item.id) # append the id in the id list
            print(ex_var_list)
            if product_variation in ex_var_list: # if the product_variation is in the ex_var_list, then increase the quantity by 1
                # increase the cart_item quantity by 1
                index = ex_var_list.index(product_variation) # get the index of the product_variation
                item_id = id[index] # get the id of the cart_item using the index
                item = CartItem.objects.get(product=product, id=item_id) # get the cart_item using the product and id
                item.quantity += 1 # increase the quantity by 1
                item.save() # save the cart_item
            else: # if the product_variation is not in the ex_var_list, then create the cart_item
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart,
                )
                if len(product_variation) > 0:  # if the product_variation is greater than 0, then the product has variation
                    item.variation.clear()  # clear the cart_item variation
                    item.variation.add(*product_variation) # add the variation in the cart_item, * mark is used to iterate over the product_variation
            # cart_item.quantity += 1  # if the cart_item already exists, then increase the quantity by 1
                item.save()
        else:  # if the cart_item does not exist, then create the cart_item
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )  # create the cart_item
            if len(product_variation) > 0:  # if the product_variation is greater than 0, then the product has variation
                cart_item.variation.clear()  # clear the cart_item variation
                cart_item.variation.add(*product_variation) # add the variation in the cart_item, * mark is used to iterate over the product_variation
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id,cart_item_id):  # remove_cart() is used to remove the cart_item from the cart for (-) button
    product = get_object_or_404(Product, id=product_id)  # get the product
    try: # try to get the cart_item
        if request.user.is_authenticated:  # check if the user is authenticated or not
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id) # if user is authenticated, then get the cart_item using the product and user
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id )  # get the cart_item using the product and cart
        if cart_item.quantity > 1:  # if the quantity of the cart_item is greater than 1
            cart_item.quantity -= 1  # then decrease the quantity by 1
            cart_item.save()  # save the cart_item
        else:
            cart_item.delete()  # else delete the cart_item
    except:
        pass
    return redirect('cart')


def remove_cart_item(request,
                     product_id,cart_item_id):  # remove_cart_item() is used to remove the cart_item from the cart for (x) button
    product = get_object_or_404(Product, id=product_id)  # get the product
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)  # get the cart_item using the product and cart
    cart_item.delete()  # delete the cart_item
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:  # check if the user is authenticated or not
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)  # if user is authenticated, then get the cart items with the user
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # get all the cart_items of a particular cart
        for cart_item in cart_items:  # iterate over the cart_items
            total += (cart_item.product.price * cart_item.quantity)  # calculate the total
            quantity += cart_item.quantity  # calculate the total quantity
        tax = (2 * total) / 100  # calculate the tax
        grand_total = total + tax  # calculate the grand total
    except ObjectDoesNotExist:  # if the cart does not exist, then just ignore
        pass  # just ignore
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login') # it also give us next url for checkout page
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
            tax = 0
            grand_total = 0
            if request.user.is_authenticated:  # check if the user is authenticated or not
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)  # if user is authenticated, then get the cart items with the user
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # get all the cart_items of a particular cart
            for cart_item in cart_items:  # iterate over the cart_items
                total += (cart_item.product.price * cart_item.quantity)  # calculate the total
                quantity += cart_item.quantity  # calculate the total quantity
            tax = (2 * total) / 100  # calculate the tax
            grand_total = total + tax  # calculate the grand total
    except ObjectDoesNotExist:  # if the cart does not exist, then just ignore
            pass
    context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'tax': tax,
            'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)